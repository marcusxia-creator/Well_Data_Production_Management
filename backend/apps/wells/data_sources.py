import re

import psycopg
from django.conf import settings
from psycopg import sql


SAFE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
COLUMN_ALIASES = {
    "uwi": ["base_uwi", "user_format_well_id", "api", "well_number", "well_no"],
    "name": ["well_name", "lease_name", "last_permit_lease_name", "well_number", "well_no"],
    "latitude": ["latitude", "lat83", "surf_hole_latitude_nad83", "lat27"],
    "longitude": ["longitude", "long83", "surf_hole_longitude_nad83", "long27"],
    "operator": ["cur_operator_name", "current_operator", "operator", "last_permit_operator"],
    "well_type": ["well_type", "symbol_desc", "symbol"],
    "status": ["well_status_text", "wellbore_status", "prod_status_text", "symbol_desc"],
}


def connection_kwargs(database_name):
    config = settings.DATABASES["default"]
    return {
        "dbname": database_name,
        "user": config["USER"],
        "password": config["PASSWORD"],
        "host": config["HOST"],
        "port": config["PORT"],
        "connect_timeout": 5,
    }


def validate_name(value):
    if not SAFE_NAME.fullmatch(value or ""):
        raise ValueError(f"Invalid database identifier: {value!r}")
    return value


def available_databases():
    current = settings.DATABASES["default"]["NAME"]
    with psycopg.connect(**connection_kwargs(current)) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT datname FROM pg_database WHERE datallowconn AND NOT datistemplate ORDER BY datname")
            return [row[0] for row in cursor.fetchall()]


def table_columns(database_name):
    validate_name(database_name)
    with psycopg.connect(**connection_kwargs(database_name)) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
                """
            )
            tables = {}
            for table_name, column_name in cursor.fetchall():
                tables.setdefault(table_name, []).append(column_name)
            return tables


def resolved_columns(columns):
    lookup = {column.casefold(): column for column in columns}
    return {
        field: next((lookup[alias] for alias in aliases if alias in lookup), None)
        for field, aliases in COLUMN_ALIASES.items()
    }


def compatible_tables(database_name):
    compatible = []
    for table_name, columns in table_columns(database_name).items():
        resolved = resolved_columns(columns)
        if resolved["uwi"] and resolved["latitude"] and resolved["longitude"]:
            compatible.append({
                "value": table_name,
                "label": table_name,
                "columns": resolved,
            })
    return compatible


def ensure_compatible_source(database_name, table_name):
    validate_name(database_name)
    validate_name(table_name)
    tables = table_columns(database_name)
    if table_name not in tables:
        raise ValueError("The selected table does not exist.")
    resolved = resolved_columns(tables[table_name])
    if not all(resolved[field] for field in ("uwi", "latitude", "longitude")):
        raise ValueError("The selected table must contain a well identifier, latitude, and longitude.")
    return resolved


def category_for_status(status_text):
    value = (status_text or "").casefold()
    if "abd" in value or "plug" in value:
        return "ABD"
    if "susp" in value:
        return "Suspended"
    return "Active"


def source_options(database_name, table_name):
    columns = ensure_compatible_source(database_name, table_name)
    fields = {
        "operators": columns["operator"],
        "types": columns["well_type"],
        "actual_statuses": columns["status"],
    }
    payload = {"operators": [], "types": [], "actual_statuses": [], "statuses": [], "formations": []}
    with psycopg.connect(**connection_kwargs(database_name)) as connection:
        with connection.cursor() as cursor:
            for key, column_name in fields.items():
                if not column_name:
                    continue
                cursor.execute(
                    sql.SQL("SELECT DISTINCT {}::text FROM {} WHERE {} IS NOT NULL AND btrim({}::text) <> '' ORDER BY 1").format(
                        sql.Identifier(column_name), sql.Identifier(table_name),
                        sql.Identifier(column_name), sql.Identifier(column_name),
                    )
                )
                payload[key] = [row[0] for row in cursor.fetchall()]
    payload["statuses"] = sorted({category_for_status(value) for value in payload["actual_statuses"]})
    return payload


def source_wells(database_name, table_name, params, limit=100):
    columns = ensure_compatible_source(database_name, table_name)
    conditions = []
    values = []

    def add_exact(param_name, field_name):
        value = params.get(param_name)
        column_name = columns.get(field_name)
        if value and column_name:
            conditions.append(sql.SQL("{}::text = %s").format(sql.Identifier(column_name)))
            values.append(value)

    add_exact("actual_status", "status")
    add_exact("well_type", "well_type")
    add_exact("cur_operator_name", "operator")

    search = params.get("search")
    if search:
        search_columns = [columns.get(field) for field in ("uwi", "name", "operator") if columns.get(field)]
        conditions.append(sql.SQL("(") + sql.SQL(" OR ").join(
            sql.SQL("{}::text ILIKE %s").format(sql.Identifier(column)) for column in search_columns
        ) + sql.SQL(")"))
        values.extend([f"%{search}%"] * len(search_columns))

    status_category = params.get("status")
    status_column = columns.get("status")
    if status_category and status_column:
        status_sql = sql.SQL("lower(COALESCE({}::text, ''))").format(sql.Identifier(status_column))
        if status_category == "ABD":
            conditions.append(sql.SQL("({0} LIKE '%%abd%%' OR {0} LIKE '%%plug%%')").format(status_sql))
        elif status_category == "Suspended":
            conditions.append(sql.SQL("{} LIKE '%%susp%%'").format(status_sql))
        elif status_category == "Active":
            conditions.append(sql.SQL("({0} NOT LIKE '%%abd%%' AND {0} NOT LIKE '%%plug%%' AND {0} NOT LIKE '%%susp%%')").format(status_sql))

    where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")
    select_fields = []
    for field in ("uwi", "name", "latitude", "longitude", "operator", "well_type", "status"):
        column_name = columns.get(field)
        if column_name:
            select_fields.append(sql.SQL("{}::text AS {}").format(sql.Identifier(column_name), sql.Identifier(field)))
        else:
            select_fields.append(sql.SQL("NULL::text AS {}").format(sql.Identifier(field)))

    with psycopg.connect(**connection_kwargs(database_name)) as connection:
        with connection.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute(sql.SQL("SELECT count(*) FROM {}{}").format(sql.Identifier(table_name), where_clause), values)
            count = cursor.fetchone()["count"]
            cursor.execute(
                sql.SQL("SELECT {} FROM {}{} LIMIT %s").format(
                    sql.SQL(", ").join(select_fields), sql.Identifier(table_name), where_clause,
                ),
                [*values, limit],
            )
            rows = cursor.fetchall()

    results = []
    for index, row in enumerate(rows):
        try:
            latitude = float(row["latitude"]) if row["latitude"] not in (None, "") else None
            longitude = float(row["longitude"]) if row["longitude"] not in (None, "") else None
        except (TypeError, ValueError):
            latitude = longitude = None
        actual_status = row["status"] or "Unknown"
        results.append({
            "id": row["uwi"] or f"row-{index}",
            "uwi": row["uwi"] or f"row-{index}",
            "name": row["name"] or row["uwi"] or "Unnamed well",
            "operator": row["operator"],
            "status": category_for_status(actual_status),
            "actual_status_text": actual_status,
            "well_type": row["well_type"],
            "latitude": latitude,
            "longitude": longitude,
        })
    return {"count": count, "next": None, "previous": None, "results": results}
