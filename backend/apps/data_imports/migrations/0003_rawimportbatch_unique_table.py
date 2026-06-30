from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_imports", "0002_rawimportbatch_raw_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawimportbatch",
            name="unique_table_name",
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name="rawimportbatch",
            name="unique_table_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="rawimportbatch",
            name="unique_row_count",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
