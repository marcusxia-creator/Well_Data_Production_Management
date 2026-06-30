from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_imports", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawimportbatch",
            name="raw_table_name",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="rawimportbatch",
            name="raw_table_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
