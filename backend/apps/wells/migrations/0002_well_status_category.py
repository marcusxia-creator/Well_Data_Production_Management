from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wells", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WellStatusCategory",
            fields=[
                (
                    "base_uwi",
                    models.TextField(primary_key=True, serialize=False),
                ),
                ("status_category", models.CharField(db_index=True, max_length=32)),
                ("actual_status_text", models.TextField(blank=True, db_index=True, null=True)),
                ("last_production_date", models.DateField(blank=True, null=True)),
                ("last_injection_date", models.DateField(blank=True, null=True)),
                ("refreshed_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "well_status_category",
                "indexes": [
                    models.Index(fields=["status_category", "actual_status_text"], name="wells_well__status__b25d95_idx")
                ],
            },
        ),
    ]
