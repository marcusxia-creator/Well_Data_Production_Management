#Well Production Management

Independent Django, React, PostgreSQL, and PostGIS application for loading and exploring a separate well-production dataset.

This project is a clean copy of the wellbore platform. It uses its own Docker Compose project, PostgreSQL database, persistent volume, and network ports. Running it does not modify the original `Django_PostgreSql_React` database or containers.

## Services

| Service | Local address |
| --- | --- |
| React dashboard | http://localhost:5174 |
| Django API | http://localhost:8001/api/wells/ |
| Django admin | http://localhost:8001/admin/ |
| PostgreSQL/PostGIS | localhost:5433 |

Database defaults:

```text
Database: sp_well_production_db
User:     sp_app
Password: sp_dev_password
Host inside Docker: db
Host from Windows:  localhost
Port inside Docker: 5432
Port from Windows:   5433
```

These credentials are for local development only. Change them in `.env` before using the application outside your computer.

## First Startup

Open PowerShell:

```powershell
cd C:\Users\gxia\Python\SP_Petroleum_Well_Production_Management
docker compose up -d --build
```

Watch startup:

```powershell
docker compose logs -f
```

The first startup automatically:

1. Creates the `sp_well_production_db` PostgreSQL database.
2. Enables PostGIS.
3. Creates empty source tables such as `well_header` and `well_production_summary`.
4. Runs Django migrations for authentication, admin, and cache tables.
5. Starts the API and dashboard.

The dashboard initially shows zero wells because the SP dataset has not yet been imported.


## Platform Modules

The platform is divided into two independent top-level sections. Use the module navigation in the product header or open the section URL directly.

### 1. Raw Data Import & Mapping

```text
http://localhost:5174/#data-import
```

This module uses two sequential pages:

1. **Raw Excel Import**: choose an `.xlsx` or `.xlsm` workbook. The first worksheet is read, column names are cleaned to lowercase `snake_case`, and every non-empty row is initially stored in PostgreSQL as JSON. Review the cleaned headings and raw-table preview. Clicking **Next: Column Mapping** creates a physical table named `raw_excel_batch_<batch_id>` with one text column per cleaned Excel heading, then opens the mapping page.
2. **Raw Data Table Column Mapping**: manually link cleaned source columns to target columns. Exact matches from `backend/megadata/table_column_mapping_working.csv` are suggested automatically. Use **Next: Review Mapped Data** to save the mapping and open a non-destructive review page.`r`n3. **Mapped Data Review**: select each target table and review its mapped headers and first 20 transformed rows. This preview does not write target tables. Use **Complete Process** only after the preview is correct.

Header cleaning removes surrounding spaces and punctuation, converts words to lowercase underscore names, makes duplicate names unique with suffixes such as `__2`, assigns names to blank headings, and prefixes headings that begin with numbers.

Every new upload also generates three lineage columns before preview and mapping:

- import_timestamp: one timestamp identifying when the batch was uploaded
- 
aw_id: a generated unique bigint for each raw row
- source_file: the uploaded Excel filename

These fields are automatically suggested for the common mapping rules and are created in the physical raw table as 	imestamptz, igint, and 	ext.

Import metadata is stored in:

```text
raw_import_batch
raw_import_row
raw_import_column_mapping
```

Each upload receives its own editable copy of all mapping rules. The original CSV remains the template for future imports.

Casing mappings are grouped by `casing_type` and create separate `well_casing` rows. Other target groups create one output row per raw Excel row when at least one table-specific value is present.

The **Replace existing target-table data** option is enabled by default. Disable it only when intentionally appending compatible data.

After a successful split, refresh dashboard caches:

```powershell
docker compose exec backend python manage.py refresh_well_status_categories
docker compose exec backend python manage.py refresh_well_production_formations
docker compose exec backend python manage.py refresh_well_current_operators
```

### 2. Well Production Dashboard

```text
http://localhost:5174/#dashboard
```

This module contains only operational well views: map, filters, counts, searchable operator selection, formations, and the well register. Import controls do not appear inside the dashboard.

## Source Tables

The import schema is created by:

```text
deployment/initdb/001_source_schema.sql
```

Expected source tables:

```text
well_header
well_location
well_status
well_drilling
well_casing
well_production_summary
wellstor_all
```

The dashboard uses `base_uwi` to connect records between source tables. For duplicated base UWIs, the application uses the greatest suffix and then the newest `raw_id`.

## Importing A PostgreSQL Dump

Copy a dump into this project, for example `database_dumps\sp.dump`. The `database_dumps` directory and `*.dump` files are ignored by Git.

Restore a custom-format dump:

```powershell
docker compose exec -T db pg_restore --username=sp_app --dbname=sp_well_production_db --clean --if-exists --no-owner < database_dumps\sp.dump
```

Restore a plain SQL file:

```powershell
docker compose exec -T db psql --username=sp_app --dbname=sp_well_production_db < database_dumps\sp.sql
```

If the incoming dataset uses different table or column names, update the import process or Django models before refreshing caches.

## Importing CSV Files

A CSV can be copied into the database container and imported with PostgreSQL `\copy`. Example:

```powershell
docker compose cp C:\path\to\well_header.csv db:/tmp/well_header.csv
docker compose exec db psql -U sp_app -d sp_well_production_db -c "\copy well_header FROM '/tmp/well_header.csv' WITH (FORMAT csv, HEADER true)"
```

Repeat for each source table. CSV headings must match the database columns.

## Refreshing Cached Filters

After every dataset import, run:

```powershell
docker compose exec backend python manage.py refresh_well_status_categories
docker compose exec backend python manage.py refresh_well_production_formations
docker compose exec backend python manage.py refresh_well_current_operators
```

These commands populate:

```text
well_status_category
well_production_formation
well_current_operator
```

The current-operator cache creates one operator per collapsed `base_uwi`. The dashboard operator field supports searchable single selection.

## Useful Commands

Check containers:

```powershell
docker compose ps
```

Open PostgreSQL:

```powershell
docker compose exec db psql -U sp_app -d sp_well_production_db
```

Run Django checks:

```powershell
docker compose exec backend python manage.py check
```

Create an admin user:

```powershell
docker compose exec backend python manage.py createsuperuser
```

Stop the application:

```powershell
docker compose down
```

Stop and permanently delete only this project's Docker database volume:

```powershell
docker compose down -v
```

The `-v` command deletes imported SP database data. Use it only when intentionally resetting the new database.

## API Filters

```text
GET /api/wells/
GET /api/current-operators/
GET /api/well-statuses/
GET /api/actual-well-statuses/
GET /api/well-types/
GET /api/production-injection-formations/
```

Examples:

```text
/api/wells/?cur_operator_name=Example%20Energy%20Ltd
/api/wells/?status=Active
/api/wells/?well_type=OIL
/api/wells/?prod_inject_frmtn=FormationName
```

## Google Maps

OpenStreetMap works without a key. To enable Google Map and Google Satellite, set `VITE_GOOGLE_MAPS_API_KEY` in `.env`, then rebuild the frontend:

```powershell
docker compose up -d --build frontend
```
