from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone


class Command(BaseCommand):
    help = "Refresh sliced production/injection formation values for fast filtering."

    def handle(self, *args, **options):
        sql = """
        TRUNCATE TABLE well_production_formation;

        INSERT INTO well_production_formation (
            base_uwi,
            formation,
            source_value,
            suffix,
            refreshed_at
        )
        WITH selected_production AS (
            SELECT DISTINCT ON (base_uwi)
                base_uwi,
                suffix,
                raw_id,
                prod_inject_frmtn
            FROM well_production_summary
            WHERE base_uwi IS NOT NULL
              AND prod_inject_frmtn IS NOT NULL
              AND btrim(prod_inject_frmtn) <> ''
            ORDER BY base_uwi, suffix DESC NULLS LAST, raw_id DESC NULLS LAST
        ),
        sliced AS (
            SELECT
                base_uwi,
                btrim(formation_part) AS formation,
                prod_inject_frmtn AS source_value,
                suffix
            FROM selected_production,
            regexp_split_to_table(prod_inject_frmtn, ';') AS formation_part
        )
        SELECT DISTINCT ON (base_uwi, formation)
            base_uwi,
            formation,
            source_value,
            suffix,
            %s AS refreshed_at
        FROM sliced
        WHERE formation <> ''
        ORDER BY base_uwi, formation, suffix DESC NULLS LAST;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql, [timezone.now()])
            cursor.execute("SELECT COUNT(*) FROM well_production_formation")
            mapping_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT formation) FROM well_production_formation")
            formation_count = cursor.fetchone()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"Refreshed {mapping_count} well-formation mappings across {formation_count} unique formations."
            )
        )
