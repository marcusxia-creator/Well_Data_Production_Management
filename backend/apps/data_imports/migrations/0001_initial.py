from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="RawImportBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file_name", models.TextField()),
                ("sheet_name", models.TextField()),
                ("status", models.CharField(choices=[("uploaded", "Uploaded"), ("mapped", "Mapped"), ("completed", "Completed"), ("failed", "Failed")], db_index=True, default="uploaded", max_length=24)),
                ("headers", models.JSONField(default=list)),
                ("row_count", models.PositiveIntegerField(default=0)),
                ("imported_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("error_message", models.TextField(blank=True)),
                ("result_summary", models.JSONField(blank=True, default=dict)),
            ],
            options={"db_table": "raw_import_batch", "ordering": ["-imported_at"]},
        ),
        migrations.CreateModel(
            name="RawImportRow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("row_number", models.PositiveIntegerField()),
                ("data", models.JSONField(default=dict)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rows", to="data_imports.rawimportbatch")),
            ],
            options={"db_table": "raw_import_row", "ordering": ["row_number"]},
        ),
        migrations.CreateModel(
            name="ImportColumnMapping",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mapping_order", models.PositiveIntegerField()),
                ("target_table", models.CharField(db_index=True, max_length=128)),
                ("target_column", models.CharField(max_length=160)),
                ("target_type", models.CharField(default="text", max_length=64)),
                ("suggested_source_column", models.TextField(blank=True)),
                ("source_column", models.TextField(blank=True)),
                ("transform_rule", models.TextField(blank=True)),
                ("casing_type", models.CharField(blank=True, max_length=80)),
                ("include", models.BooleanField(default=True)),
                ("required", models.BooleanField(default=False)),
                ("default_value", models.TextField(blank=True)),
                ("key_role", models.CharField(blank=True, max_length=80)),
                ("notes", models.TextField(blank=True)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mappings", to="data_imports.rawimportbatch")),
            ],
            options={"db_table": "raw_import_column_mapping", "ordering": ["mapping_order"]},
        ),
        migrations.AddConstraint(model_name="rawimportrow", constraint=models.UniqueConstraint(fields=("batch", "row_number"), name="raw_import_batch_row_unique")),
        migrations.AddConstraint(model_name="importcolumnmapping", constraint=models.UniqueConstraint(fields=("batch", "mapping_order"), name="raw_import_mapping_order_unique")),
    ]
