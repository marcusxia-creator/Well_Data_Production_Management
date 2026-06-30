from django.db import migrations


FORWARD_SQL = """
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS cur_operator_code text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS cur_operator_name text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS lahee_class_code text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS lic_subs_well_obj text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS lic_wa_wid_permit text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS org_operator_name text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS orig_operator_code text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS orig_units_m_api text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS well_pad_id text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS well_type text;
ALTER TABLE well_status ADD COLUMN IF NOT EXISTS "Permit_id" text;

DO $migration$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'well_header'
          AND column_name = 'cur_operator_name'
    ) THEN
        EXECUTE $copy$
            UPDATE well_status AS status
            SET cur_operator_code = header.cur_operator_code,
                cur_operator_name = header.cur_operator_name,
                lahee_class_code = header.lahee_class_code,
                lic_subs_well_obj = header.lic_subs_well_obj,
                lic_wa_wid_permit = header.lic_wa_wid_permit,
                org_operator_name = header.org_operator_name,
                orig_operator_code = header.orig_operator_code,
                orig_units_m_api = header.orig_units_m_api,
                well_pad_id = header.well_pad_id,
                well_type = header.well_type,
                "Permit_id" = header."Permit_id"
            FROM well_header AS header
            WHERE status.raw_id = header.raw_id
        $copy$;
    END IF;
END
$migration$;

DELETE FROM well_header WHERE NULLIF(BTRIM(base_uwi), '') IS NULL;
DELETE FROM well_header AS duplicate
USING (
    SELECT ctid, ROW_NUMBER() OVER (
        PARTITION BY base_uwi
        ORDER BY suffix DESC NULLS LAST, raw_id DESC NULLS LAST, ctid DESC
    ) AS row_number
    FROM well_header
) AS ranked
WHERE duplicate.ctid = ranked.ctid AND ranked.row_number > 1;

DROP INDEX IF EXISTS well_header_operator_idx;
DROP INDEX IF EXISTS well_header_type_idx;
DROP INDEX IF EXISTS well_header_base_uwi_idx;
ALTER TABLE well_header DROP COLUMN IF EXISTS cur_operator_code;
ALTER TABLE well_header DROP COLUMN IF EXISTS cur_operator_name;
ALTER TABLE well_header DROP COLUMN IF EXISTS lahee_class_code;
ALTER TABLE well_header DROP COLUMN IF EXISTS lic_subs_well_obj;
ALTER TABLE well_header DROP COLUMN IF EXISTS lic_wa_wid_permit;
ALTER TABLE well_header DROP COLUMN IF EXISTS org_operator_name;
ALTER TABLE well_header DROP COLUMN IF EXISTS orig_operator_code;
ALTER TABLE well_header DROP COLUMN IF EXISTS orig_units_m_api;
ALTER TABLE well_header DROP COLUMN IF EXISTS well_pad_id;
ALTER TABLE well_header DROP COLUMN IF EXISTS well_type;
ALTER TABLE well_header DROP COLUMN IF EXISTS "Permit_id";
CREATE UNIQUE INDEX IF NOT EXISTS well_header_base_uwi_unique_idx ON well_header (base_uwi);
CREATE INDEX IF NOT EXISTS well_status_operator_idx ON well_status (cur_operator_name);
CREATE INDEX IF NOT EXISTS well_status_type_idx ON well_status (well_type);
"""


class Migration(migrations.Migration):
    dependencies = [
        ("wells", "0004_well_current_operator"),
    ]

    operations = [
        migrations.RunSQL(FORWARD_SQL, reverse_sql=migrations.RunSQL.noop),
    ]