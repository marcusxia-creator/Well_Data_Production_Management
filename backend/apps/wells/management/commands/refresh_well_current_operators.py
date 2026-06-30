from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Refresh the current operator cache for fast dashboard filtering."

    def handle(self, *args, **options):
        sql = """
        TRUNCATE TABLE well_current_operator;

        INSERT INTO well_current_operator (
            base_uwi,
            operator_name,
            suffix,
            raw_id,
            refreshed_at
        )
        SELECT
            base_uwi,
            btrim(cur_operator_name),
            suffix,
            raw_id,
            %s AS refreshed_at
        FROM (
            SELECT DISTINCT ON (base_uwi)
                base_uwi,
                cur_operator_name,
                suffix,
                raw_id
            FROM well_status
            WHERE base_uwi IS NOT NULL
            ORDER BY base_uwi, suffix DESC NULLS LAST, raw_id DESC NULLS LAST
        ) AS selected_headers
        WHERE cur_operator_name IS NOT NULL
          AND btrim(cur_operator_name) <> '';
        """

        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute(sql, [timezone.now()])
            cursor.execute("SELECT COUNT(*) FROM well_current_operator")
            mapping_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT operator_name) FROM well_current_operator")
            operator_count = cursor.fetchone()[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"Refreshed {mapping_count} well-operator mappings across {operator_count} unique operators."
            )
        )
