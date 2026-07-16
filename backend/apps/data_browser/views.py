from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from config.permissions import IsNotRestrictedViewer

from .services import available_databases, delete_table, table_catalog, table_rows


@api_view(["GET"])
@permission_classes([IsNotRestrictedViewer])
def databases(request):
    try:
        database_names = available_databases()
    except Exception as exc:
        return Response({"detail": str(exc)}, status=400)

    payload = []
    for database_name in database_names:
        try:
            payload.append({"name": database_name, "tables": table_catalog(database_name)})
        except Exception as exc:
            payload.append({"name": database_name, "tables": [], "error": str(exc)})

    return Response({
        "current_database": settings.DATABASES["default"]["NAME"],
        "databases": payload,
    })


@api_view(["GET"])
@permission_classes([IsNotRestrictedViewer])
def query_table(request):
    database_name = request.query_params.get("database")
    table_name = request.query_params.get("table")
    if not database_name or not table_name:
        return Response({"detail": "Select a database and table."}, status=400)

    try:
        return Response(table_rows(database_name, table_name, request.query_params))
    except Exception as exc:
        return Response({"detail": str(exc)}, status=400)

@api_view(["DELETE"])
@permission_classes([IsNotRestrictedViewer])
def delete_data_table(request):
    database_name = request.data.get("database")
    table_name = request.data.get("table")
    confirmation = request.data.get("confirmation")
    if not database_name or not table_name:
        return Response({"detail": "Select a database and table."}, status=400)
    if confirmation != table_name:
        return Response({"detail": "Enter the exact table name to confirm deletion."}, status=400)

    try:
        return Response(delete_table(database_name, table_name))
    except Exception as exc:
        return Response({"detail": str(exc)}, status=400)
