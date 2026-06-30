# Generated for reusable raw import mapping templates.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("data_imports", "0003_rawimportbatch_unique_table"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImportMappingTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160, unique=True)),
                ("source_headers", models.JSONField(default=list)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "raw_import_mapping_template",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ImportMappingTemplateColumn",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("mapping_order", models.PositiveIntegerField()),
                ("target_table", models.CharField(db_index=True, max_length=128)),
                ("target_column", models.CharField(max_length=160)),
                ("target_type", models.CharField(default="text", max_length=64)),
                ("source_column", models.TextField(blank=True)),
                ("transform_rule", models.TextField(blank=True)),
                ("casing_type", models.CharField(blank=True, max_length=80)),
                ("include", models.BooleanField(default=True)),
                ("required", models.BooleanField(default=False)),
                ("default_value", models.TextField(blank=True)),
                ("key_role", models.CharField(blank=True, max_length=80)),
                ("notes", models.TextField(blank=True)),
                ("template", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="columns", to="data_imports.importmappingtemplate")),
            ],
            options={
                "db_table": "raw_import_mapping_template_column",
                "ordering": ["mapping_order"],
            },
        ),
        migrations.AddConstraint(
            model_name="importmappingtemplatecolumn",
            constraint=models.UniqueConstraint(fields=("template", "mapping_order"), name="raw_import_template_mapping_order_unique"),
        ),
    ]
