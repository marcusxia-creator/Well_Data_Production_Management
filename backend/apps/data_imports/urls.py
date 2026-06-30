from django.urls import path

from .views import apply_mapping_template, create_raw_table, create_unique_table, execute_split, import_batch_detail, import_batches, mapped_preview, mapping_templates, save_mapping_template, update_mappings, upload_workbook


urlpatterns = [
    path("batches/", import_batches, name="import-batches"),
    path("upload/", upload_workbook, name="import-upload"),
    path("mapping-templates/", mapping_templates, name="import-mapping-templates"),
    path("batches/<int:batch_id>/", import_batch_detail, name="import-batch-detail"),
    path("batches/<int:batch_id>/raw-table/", create_raw_table, name="import-raw-table"),
    path("batches/<int:batch_id>/unique-table/", create_unique_table, name="import-unique-table"),
    path("batches/<int:batch_id>/mappings/", update_mappings, name="import-mappings"),
    path("batches/<int:batch_id>/mapping-templates/", save_mapping_template, name="import-save-mapping-template"),
    path("batches/<int:batch_id>/apply-mapping-template/", apply_mapping_template, name="import-apply-mapping-template"),
    path("batches/<int:batch_id>/mapped-preview/", mapped_preview, name="import-mapped-preview"),
    path("batches/<int:batch_id>/execute/", execute_split, name="import-execute"),
]
