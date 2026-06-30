from django.db import models


class RawImportBatch(models.Model):
    STATUS_UPLOADED = "uploaded"
    STATUS_MAPPED = "mapped"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [(STATUS_UPLOADED, "Uploaded"), (STATUS_MAPPED, "Mapped"), (STATUS_COMPLETED, "Completed"), (STATUS_FAILED, "Failed")]

    file_name = models.TextField()
    sheet_name = models.TextField()
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_UPLOADED, db_index=True)
    headers = models.JSONField(default=list)
    row_count = models.PositiveIntegerField(default=0)
    raw_table_name = models.CharField(max_length=128, blank=True)
    raw_table_created_at = models.DateTimeField(blank=True, null=True)
    unique_table_name = models.CharField(max_length=128, blank=True)
    unique_table_created_at = models.DateTimeField(blank=True, null=True)
    unique_row_count = models.PositiveIntegerField(default=0)
    imported_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    result_summary = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "raw_import_batch"
        ordering = ["-imported_at"]

    def __str__(self):
        return f"{self.file_name} ({self.row_count} rows)"


class RawImportRow(models.Model):
    batch = models.ForeignKey(RawImportBatch, on_delete=models.CASCADE, related_name="rows")
    row_number = models.PositiveIntegerField()
    data = models.JSONField(default=dict)

    class Meta:
        db_table = "raw_import_row"
        ordering = ["row_number"]
        constraints = [models.UniqueConstraint(fields=["batch", "row_number"], name="raw_import_batch_row_unique")]


class ImportColumnMapping(models.Model):
    batch = models.ForeignKey(RawImportBatch, on_delete=models.CASCADE, related_name="mappings")
    mapping_order = models.PositiveIntegerField()
    target_table = models.CharField(max_length=128, db_index=True)
    target_column = models.CharField(max_length=160)
    target_type = models.CharField(max_length=64, default="text")
    suggested_source_column = models.TextField(blank=True)
    source_column = models.TextField(blank=True)
    transform_rule = models.TextField(blank=True)
    casing_type = models.CharField(max_length=80, blank=True)
    include = models.BooleanField(default=True)
    required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    key_role = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "raw_import_column_mapping"
        ordering = ["mapping_order"]
        constraints = [models.UniqueConstraint(fields=["batch", "mapping_order"], name="raw_import_mapping_order_unique")]

    def __str__(self):
        return f"{self.target_table}.{self.target_column} <- {self.source_column or '(unmapped)'}"

class ImportMappingTemplate(models.Model):
    name = models.CharField(max_length=160, unique=True)
    source_headers = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_import_mapping_template"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ImportMappingTemplateColumn(models.Model):
    template = models.ForeignKey(ImportMappingTemplate, on_delete=models.CASCADE, related_name="columns")
    mapping_order = models.PositiveIntegerField()
    target_table = models.CharField(max_length=128, db_index=True)
    target_column = models.CharField(max_length=160)
    target_type = models.CharField(max_length=64, default="text")
    source_column = models.TextField(blank=True)
    transform_rule = models.TextField(blank=True)
    casing_type = models.CharField(max_length=80, blank=True)
    include = models.BooleanField(default=True)
    required = models.BooleanField(default=False)
    default_value = models.TextField(blank=True)
    key_role = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "raw_import_mapping_template_column"
        ordering = ["mapping_order"]
        constraints = [models.UniqueConstraint(fields=["template", "mapping_order"], name="raw_import_template_mapping_order_unique")]

    def __str__(self):
        return f"{self.template.name}: {self.target_table}.{self.target_column}"

