from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wells", "0003_well_production_formation"),
    ]

    operations = [
        migrations.CreateModel(
            name="WellCurrentOperator",
            fields=[
                ("base_uwi", models.TextField(primary_key=True, serialize=False)),
                ("operator_name", models.TextField(db_index=True)),
                ("suffix", models.TextField(blank=True, null=True)),
                ("raw_id", models.BigIntegerField(blank=True, null=True)),
                ("refreshed_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "well_current_operator",
                "indexes": [
                    models.Index(
                        fields=["operator_name", "base_uwi"],
                        name="wells_well__operato_9176c2_idx",
                    ),
                ],
            },
        ),
    ]
