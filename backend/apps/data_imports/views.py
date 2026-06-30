from django.core.management import call_command
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from .models import ImportColumnMapping, ImportMappingTemplate, RawImportBatch
from .services import apply_mapping_template_to_batch, create_unique_api_table, ingest_workbook, materialize_raw_table, preview_mapped_batch, save_mapping_template_from_batch, serialize_batch, serialize_mapping_template, split_batch


@api_view(["GET"])
def import_batches(request):
    batches = RawImportBatch.objects.all()[:50]
    return Response([
        {
            "id": batch.id,
            "file_name": batch.file_name,
            "sheet_name": batch.sheet_name,
            "status": batch.status,
            "row_count": batch.row_count,
            "raw_table_name": batch.raw_table_name,
            "unique_table_name": batch.unique_table_name,
            "unique_row_count": batch.unique_row_count,
            "imported_at": batch.imported_at,
            "completed_at": batch.completed_at,
        }
        for batch in batches
    ])


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_workbook(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"detail": "Choose an Excel workbook."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        batch = ingest_workbook(uploaded_file, request.data.get("sheet_name", "").strip())
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serialize_batch(batch, include_mappings=True), status=status.HTTP_201_CREATED)


@api_view(["GET"])
def import_batch_detail(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    return Response(serialize_batch(batch, include_mappings=True))


@api_view(["POST"])
def create_raw_table(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    try:
        materialize_raw_table(batch)
    except Exception as exc:
        batch.error_message = str(exc)
        batch.save(update_fields=["error_message"])
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serialize_batch(batch, include_mappings=True))


@api_view(["POST"])
def create_unique_table(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    try:
        summary = create_unique_api_table(batch, request.data.get("api_column", "api"))
    except Exception as exc:
        batch.error_message = str(exc)
        batch.save(update_fields=["error_message"])
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"batch": serialize_batch(batch, include_mappings=True), "summary": summary})


@api_view(["PUT"])
def update_mappings(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    updates = request.data.get("mappings", [])
    by_id = {mapping.id: mapping for mapping in batch.mappings.all()}
    changed = []
    for update in updates:
        mapping = by_id.get(update.get("id"))
        if not mapping:
            continue
        source_column = (update.get("source_column") or "").strip()
        if source_column and source_column not in batch.headers:
            return Response({"detail": f"Unknown source column: {source_column}"}, status=status.HTTP_400_BAD_REQUEST)
        mapping.source_column = source_column
        mapping.include = bool(update.get("include", mapping.include))
        mapping.default_value = str(update.get("default_value", mapping.default_value) or "")
        changed.append(mapping)
    if changed:
        ImportColumnMapping.objects.bulk_update(changed, ["source_column", "include", "default_value"], batch_size=500)
    batch.status = RawImportBatch.STATUS_MAPPED
    batch.error_message = ""
    batch.save(update_fields=["status", "error_message"])
    return Response(serialize_batch(batch, include_mappings=True))

@api_view(["GET"])
def mapping_templates(request):
    templates = ImportMappingTemplate.objects.prefetch_related("columns").all()
    return Response([serialize_mapping_template(template) for template in templates])


@api_view(["POST"])
def save_mapping_template(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    try:
        template = save_mapping_template_from_batch(batch, request.data.get("name", ""))
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serialize_mapping_template(template), status=status.HTTP_201_CREATED)


@api_view(["POST"])
def apply_mapping_template(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    template_id = request.data.get("template_id")
    template = get_object_or_404(ImportMappingTemplate, pk=template_id)
    try:
        summary = apply_mapping_template_to_batch(batch, template)
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"batch": serialize_batch(batch, include_mappings=True), "summary": summary})

@api_view(["GET"])
def mapped_preview(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    try:
        previews = preview_mapped_batch(batch, limit=20)
    except Exception as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"batch_id": batch.id, "tables": previews})


@api_view(["POST"])
def execute_split(request, batch_id):
    batch = get_object_or_404(RawImportBatch, pk=batch_id)
    try:
        summary = split_batch(batch, replace_existing=request.data.get("replace_existing", True) is not False)
        call_command("refresh_well_current_operators")
        call_command("refresh_well_status_categories")
    except Exception as exc:
        batch.status = RawImportBatch.STATUS_FAILED
        batch.error_message = str(exc)
        batch.save(update_fields=["status", "error_message"])
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"batch": serialize_batch(batch), "summary": summary})


