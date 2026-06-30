from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

class Command(BaseCommand):
    help = "Refresh derived well status categories for fast dashboard filtering."

    def handle(self, *args, **options):
        sql = """
        TRUNCATE TABLE well_status_category;

        INSERT INTO well_status_category (
            base_uwi,
            status_category,
            actual_status_text,
            last_production_date,
            last_injection_date,
            refreshed_at
        )
        WITH selected_header AS (
            SELECT DISTINCT ON (base_uwi)
                base_uwi,
                suffix,
                raw_id
            FROM well_header
            WHERE base_uwi IS NOT NULL
            ORDER BY base_uwi, suffix DESC NULLS LAST, raw_id DESC NULLS LAST
        ),
        latest_status AS (
            SELECT DISTINCT ON (base_uwi)
                base_uwi,
                suffix,
                well_status_abrv,
                well_status_text
            FROM well_status
            WHERE base_uwi IS NOT NULL
            ORDER BY base_uwi, suffix DESC NULLS LAST, raw_id DESC NULLS LAST
        ),
        production_dates AS (
            SELECT DISTINCT ON (base_uwi)
                base_uwi,
                suffix,
                GREATEST(
                    CASE
                        WHEN last_prod_yyyy_mm ~ '^[0-9]{4}[/\\-][0-9]{2}[/\\-][0-9]{2}$'
                        THEN to_date(replace(last_prod_yyyy_mm, '-', '/'), 'YYYY/MM/DD')
                        ELSE NULL
                    END,
                    on_prod_yyyy_mm_dd
                ) AS last_production_date,
                GREATEST(
                    CASE
                        WHEN last_inject_yyyy_mm ~ '^[0-9]{4}[/\\-][0-9]{2}[/\\-][0-9]{2}$'
                        THEN to_date(replace(last_inject_yyyy_mm, '-', '/'), 'YYYY/MM/DD')
                        ELSE NULL
                    END,
                    on_inject_yyyy_mm_dd
                ) AS last_injection_date
            FROM well_production_summary
            WHERE base_uwi IS NOT NULL
            ORDER BY base_uwi, suffix DESC NULLS LAST, raw_id DESC NULLS LAST
        )
        SELECT
            h.base_uwi,
            COALESCE(NULLIF(BTRIM(s.well_status_abrv), ''), 'Unknown') AS status_category,
            s.well_status_text AS actual_status_text,
            p.last_production_date,
            p.last_injection_date,
            %s AS refreshed_at
        FROM selected_header h
        LEFT JOIN latest_status s ON s.base_uwi = h.base_uwi
        LEFT JOIN production_dates p ON p.base_uwi = h.base_uwi;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, [timezone.now()])
            cursor.execute("SELECT COUNT(*) FROM well_status_category")
            count = cursor.fetchone()[0]

        self.stdout.write(self.style.SUCCESS(f"Refreshed {count} well status categories."))


