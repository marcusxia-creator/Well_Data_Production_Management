from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "No-op: this project now reads existing well data from the connected PostgreSQL database."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "No demo wells were created. The app is configured to read existing well_header data."
            )
        )
