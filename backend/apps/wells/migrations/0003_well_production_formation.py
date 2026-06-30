from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wells", "0002_well_status_category"),
    ]

    operations = [
        migrations.CreateModel(
            name="WellProductionFormation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("base_uwi", models.TextField(db_index=True)),
                ("formation", models.TextField(db_index=True)),
                ("source_value", models.TextField(blank=True, null=True)),
                ("suffix", models.TextField(blank=True, null=True)),
                ("refreshed_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "well_production_formation",
                "unique_together": {("base_uwi", "formation")},
                "indexes": [
                    models.Index(fields=["formation", "base_uwi"], name="wells_well__formati_f7df23_idx"),
                ],
            },
        ),
    ]
