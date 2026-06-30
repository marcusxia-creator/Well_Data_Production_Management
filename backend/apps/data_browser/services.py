import re

import psycopg
from django.conf import settings
from psycopg import sql
from psycopg.rows import dict_row


SAFE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MAX_PAGE_SIZE = 500
DELETABLE_TABLE_PREFIXES = ("raw_excel_batch_", "unique_raw_excel_batch_")


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


def validate_identifier(value, label="identifier"):
    if not SAFE_NAME.fullmatch(value or ""):
        raise ValueError(f"Invalid {label}: {value!r}")
    return value


def available_databases():
    current = settings.DATABASES["default"]["NAME"]
    with psycopg.connect(**connection_kwargs(current)) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT datname
                FROM pg_database
                WHERE datallowconn AND NOT datistemplate
                ORDER BY datname
                """
            )
            return [row[0] for row in cursor.fetchall()]


def table_catalog(database_name):
    validate_identifier(database_name, "database")
    with psycopg.connect(**connection_kwargs(database_name)) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    c.table_name,
                    c.column_name,
                    c.data_type,
                    c.ordinal_position,
                    COALESCE(s.n_live_tup, 0)::bigint AS estimated_rows
                FROM information_schema.columns c
                LEFT JOIN pg_stat_user_tables s
                    ON s.schemaname = c.table_schema
                    AND s.relname = c.table_name
                WHERE c.table_schema = 'public'
                ORDER BY c.table_name, c.ordinal_position
                """
            )
            tables = {}
            for row in cursor.fetchall():
                table = tables.setdefault(
                    row["table_name"],
                    {
                        "name": row["table_name"],
                        "estimated_rows": row["estimated_rows"],
                        "columns": [],
                    },
                )
                table["columns"].append(
                    {
                        "name": row["column_name"],
                        "type": row["data_type"],
                        "position": row["ordinal_position"],
                    }
                )
            return list(tables.values())


def get_table_columns(database_name, table_name):
    tables = table_catalog(database_name)
    table = next((item for item in tables if item["name"] == table_name), None)
    if not table:
        raise ValueError("The selected table does not exist.")
    return table["columns"]


def int_param(params, name, default):
    try:
        return int(params.get(name, default) or default)
    except (TypeError, ValueError):
        return default


def table_rows(database_name, table_name, params):
    validate_identifier(database_name, "database")
    validate_identifier(table_name, "table")
    columns = get_table_columns(database_name, table_name)
    column_names = [column["name"] for column in columns]

    requested_columns = params.getlist("columns") or column_names
    selected_columns = [column for column in requested_columns if column in column_names]
    if not selected_columns:
        selected_columns = column_names

    search = (params.get("search") or "").strip()
    page = max(int_param(params, "page", 1), 1)
    page_size = min(max(int_param(params, "page_size", 100), 1), MAX_PAGE_SIZE)
    offset = (page - 1) * page_size

    where_clause = sql.SQL("")
    values = []
    if search and column_names:
        search_columns = [
            sql.SQL("{}::text ILIKE %s").format(sql.Identifier(column_name))
            for column_name in column_names
        ]
        where_clause = sql.SQL(" WHERE ") + sql.SQL(" OR ").join(search_columns)
        values = [f"%{search}%"] * len(column_names)

    order_column = column_names[0]
    select_clause = sql.SQL(", ").join(
        sql.SQL("{}::text AS {}").format(sql.Identifier(column_name), sql.Identifier(column_name))
        for column_name in selected_columns
    )

    with psycopg.connect(**connection_kwargs(database_name)) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                sql.SQL("SELECT count(*) AS count FROM {}{}").format(
                    sql.Identifier(table_name),
                    where_clause,
                ),
                values,
            )
            count = cursor.fetchone()["count"]
            cursor.execute(
                sql.SQL("SELECT {} FROM {}{} ORDER BY {}::text NULLS LAST LIMIT %s OFFSET %s").format(
                    select_clause,
                    sql.Identifier(table_name),
                    where_clause,
                    sql.Identifier(order_column),
                ),
                [*values, page_size, offset],
            )
            rows = [dict(row) for row in cursor.fetchall()]

    return {
        "database": database_name,
        "table": table_name,
        "columns": [column for column in columns if column["name"] in selected_columns],
        "count": count,
        "page": page,
        "page_size": page_size,
        "next": page + 1 if offset + page_size < count else None,
        "previous": page - 1 if page > 1 else None,
        "results": rows,
    }

def delete_table(database_name, table_name):
    validate_identifier(database_name, "database")
    validate_identifier(table_name, "table")
    if not table_name.startswith(DELETABLE_TABLE_PREFIXES):
        raise ValueError("Only raw import tables can be deleted here.")

    with psycopg.connect(**connection_kwargs(database_name)) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name = %s
                )
                """,
                [table_name],
            )
            if not cursor.fetchone()[0]:
                raise ValueError("The selected table does not exist.")
            cursor.execute(
                sql.SQL("DROP TABLE {} CASCADE").format(sql.Identifier(table_name))
            )

    return {"database": database_name, "table": table_name, "deleted": True}
