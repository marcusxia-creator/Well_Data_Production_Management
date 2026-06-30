from django.contrib import admin
from .models import ImportColumnMapping, ImportMappingTemplate, ImportMappingTemplateColumn, RawImportBatch, RawImportRow


@admin.register(RawImportBatch)
class RawImportBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "sheet_name", "status", "row_count", "imported_at")
    list_filter = ("status", "imported_at")
    search_fields = ("file_name", "sheet_name")
    readonly_fields = ("headers", "result_summary", "error_message", "imported_at", "completed_at")


@admin.register(RawImportRow)
class RawImportRowAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "row_number")
    search_fields = ("batch__file_name",)
    readonly_fields = ("data",)


@admin.register(ImportColumnMapping)
class ImportColumnMappingAdmin(admin.ModelAdmin):
    list_display = ("batch", "target_table", "target_column", "source_column", "include", "required")
    list_filter = ("target_table", "include", "required")
    search_fields = ("target_column", "source_column", "suggested_source_column")

class ImportMappingTemplateColumnInline(admin.TabularInline):
    model = ImportMappingTemplateColumn
    extra = 0
    fields = ("mapping_order", "target_table", "target_column", "source_column", "include", "default_value")


@admin.register(ImportMappingTemplate)
class ImportMappingTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "updated_at", "created_at")
    search_fields = ("name",)
    readonly_fields = ("source_headers", "created_at", "updated_at")
    inlines = [ImportMappingTemplateColumnInline]

