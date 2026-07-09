from django.conf import settings
from django.db import connection
from django.db.models import FloatField, OuterRef, Q, Subquery, Value
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import ProductionMonthly, WellCurrentOperator, WellHeader, WellProductionFormation, WellStatus, WellStatusCategory
from .data_sources import available_databases, compatible_tables, source_options, source_wells
from .serializers import WellSerializer


def production_monthly_table_exists():
    return "production_monthly" in connection.introspection.table_names()


def production_daily_table_exists():
    return "production_daily" in connection.introspection.table_names()


class FastPageNumberPagination(PageNumberPagination):
    page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            page_number = max(int(page_number), 1)
        except (TypeError, ValueError):
            page_number = 1

        offset = (page_number - 1) * page_size
        self.count = queryset.count()
        rows = list(queryset[offset : offset + page_size + 1])
        self.has_next = len(rows) > page_size
        self.page_number = page_number
        return rows[:page_size]

    def get_paginated_response(self, data):
        next_page = self.page_number + 1 if self.has_next else None
        return Response(
            {
                "count": self.count,
                "next": next_page,
                "previous": self.page_number - 1 if self.page_number > 1 else None,
                "results": data,
            }
        )


class WellViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WellSerializer
    lookup_field = "base_uwi"
    pagination_class = FastPageNumberPagination

    def get_queryset(self):
        status_category = WellStatusCategory.objects.filter(base_uwi=OuterRef("base_uwi"))
        latest_status = WellStatus.objects.filter(base_uwi=OuterRef("base_uwi")).order_by(
            "-suffix", "-raw_id"
        )
        production_monthly = ProductionMonthly.objects.filter(base_uwi=OuterRef("base_uwi")).order_by("-production_month")
        if production_monthly_table_exists():
            cumulative_oil_annotation = Subquery(production_monthly.values("cumulative_oil")[:1])
            cumulative_gas_annotation = Subquery(production_monthly.values("cumulative_gas")[:1])
            cumulative_fluid_annotation = Subquery(production_monthly.values("cumulative_fluid")[:1])
        else:
            cumulative_oil_annotation = Value(None, output_field=FloatField())
            cumulative_gas_annotation = Value(None, output_field=FloatField())
            cumulative_fluid_annotation = Value(None, output_field=FloatField())
        queryset = WellHeader.objects.all().prefetch_related(
            "locations",
            "statuses",
            "drilling_records",
            "casing_records",
            "production_summaries",
        ).annotate(
            status_category_value=Subquery(status_category.values("status_category")[:1]),
            actual_status_text_value=Subquery(status_category.values("actual_status_text")[:1]),
            operator_value=Subquery(latest_status.values("cur_operator_name")[:1]),
            well_type_value=Subquery(latest_status.values("well_type")[:1]),
            cumulative_oil_volume_value=cumulative_oil_annotation,
            cumulative_gas_volume_value=cumulative_gas_annotation,
            cumulative_fluid_volume_value=cumulative_fluid_annotation,
        )
        status_value = self.request.query_params.getlist("status")
        actual_status = self.request.query_params.getlist("actual_status")
        well_type = self.request.query_params.getlist("well_type")
        operator_name = self.request.query_params.getlist("cur_operator_name")
        prod_inject_frmtn = self.request.query_params.getlist("prod_inject_frmtn")
        search = self.request.query_params.get("search")

        if status_value:
            queryset = queryset.filter(base_uwi__in=WellStatusCategory.objects.filter(
                status_category__in=status_value
            ).values("base_uwi"))
        if actual_status:
            queryset = queryset.filter(base_uwi__in=WellStatusCategory.objects.filter(
                actual_status_text__in=actual_status
            ).values("base_uwi"))
        if well_type:
            queryset = queryset.filter(base_uwi__in=WellStatus.objects.filter(
                well_type__in=well_type
            ).values("base_uwi"))
        if operator_name:
            queryset = queryset.filter(
                base_uwi__in=WellCurrentOperator.objects.filter(
                    operator_name__in=operator_name
                ).values("base_uwi")
            )
        if prod_inject_frmtn:
            queryset = queryset.filter(
                base_uwi__in=WellProductionFormation.objects.filter(
                    formation__in=prod_inject_frmtn
                ).values("base_uwi")
            )
        if search:
            queryset = queryset.filter(
                Q(base_uwi__icontains=search)
                | Q(user_format_well_id__icontains=search)
                | Q(well_name__icontains=search)
                | Q(base_uwi__in=WellStatus.objects.filter(cur_operator_name__icontains=search).values("base_uwi"))
            )

        return queryset.order_by("base_uwi", "-suffix", "-raw_id").distinct("base_uwi")

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs.get(self.lookup_field)
        obj = get_object_or_404(queryset, base_uwi=lookup_value)
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["get"], url_path="production-daily")
    def production_daily(self, request, base_uwi=None):
        well = self.get_object()
        if not production_daily_table_exists():
            return Response({"well": WellSerializer(well).data, "rows": []})

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT production_date, daily_oil, daily_water, daily_gas, fluid
                FROM production_daily
                WHERE base_uwi = %s
                ORDER BY production_date
                """,
                [well.base_uwi],
            )
            rows = [
                {
                    "date": production_date.isoformat(),
                    "daily_oil": float(daily_oil or 0),
                    "daily_water": float(daily_water or 0),
                    "daily_gas": float(daily_gas or 0),
                    "fluid": float(fluid or 0),
                }
                for production_date, daily_oil, daily_water, daily_gas, fluid in cursor.fetchall()
            ]

        return Response({"well": WellSerializer(well).data, "rows": rows})


@api_view(["GET"])
def well_statuses(request):
    statuses = (
        WellStatusCategory.objects.exclude(status_category__isnull=True)
        .exclude(status_category="")
        .order_by("status_category")
        .values_list("status_category", flat=True)
        .distinct()
    )
    return Response([{"value": status, "label": status} for status in statuses])


@api_view(["GET"])
def actual_well_statuses(request):
    queryset = WellStatusCategory.objects.exclude(actual_status_text__isnull=True).exclude(actual_status_text="")
    categories = request.query_params.getlist("status")

    if categories:
        queryset = queryset.filter(status_category__in=categories)

    statuses = (
        queryset
        .order_by("actual_status_text")
        .values_list("actual_status_text", flat=True)
        .distinct()
    )
    return Response([{"value": status, "label": status} for status in statuses])


@api_view(["GET"])
def well_types(request):
    types = (
        WellStatus.objects.exclude(well_type__isnull=True)
        .exclude(well_type="")
        .order_by("well_type")
        .values_list("well_type", flat=True)
        .distinct()
    )
    return Response([{"value": well_type, "label": well_type} for well_type in types])


@api_view(["GET"])
def production_injection_formations(request):
    formations = (
        WellProductionFormation.objects.exclude(formation__isnull=True)
        .exclude(formation="")
        .order_by("formation")
        .values_list("formation", flat=True)
        .distinct()
    )
    return Response([{"value": formation, "label": formation} for formation in formations])


@api_view(["GET"])
def current_operators(request):
    operators = (
        WellCurrentOperator.objects.exclude(operator_name__isnull=True)
        .exclude(operator_name="")
        .order_by("operator_name")
        .values_list("operator_name", flat=True)
        .distinct()
    )
    return Response([{"value": operator, "label": operator} for operator in operators])

@api_view(["GET"])
def dashboard_data_sources(request):
    current_database = settings.DATABASES["default"]["NAME"]
    databases = []
    for database_name in available_databases():
        try:
            tables = compatible_tables(database_name)
        except Exception:
            tables = []
        table_options = []
        if database_name == current_database:
            table_options.append({
                "value": "__relational__",
                "label": "Mapped relational well tables",
                "mode": "relational",
            })
        table_options.extend({**table, "mode": "flat"} for table in tables)
        if table_options:
            databases.append({"value": database_name, "label": database_name, "tables": table_options})
    return Response({"current_database": current_database, "databases": databases})


@api_view(["GET"])
def dashboard_source_options(request):
    database_name = request.query_params.get("database")
    table_name = request.query_params.get("table")
    if not database_name or not table_name or table_name == "__relational__":
        return Response({"detail": "Select a compatible flat table."}, status=400)
    try:
        options = source_options(database_name, table_name)
    except Exception as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response({
        "statuses": [{"value": value, "label": value} for value in options["statuses"]],
        "actual_statuses": [{"value": value, "label": value} for value in options["actual_statuses"]],
        "types": [{"value": value, "label": value} for value in options["types"]],
        "operators": [{"value": value, "label": value} for value in options["operators"]],
        "formations": [],
    })


@api_view(["GET"])
def dashboard_source_wells(request):
    database_name = request.query_params.get("database")
    table_name = request.query_params.get("table")
    if not database_name or not table_name or table_name == "__relational__":
        return Response({"detail": "Select a compatible flat table."}, status=400)
    try:
        payload = source_wells(database_name, table_name, request.query_params)
    except Exception as exc:
        return Response({"detail": str(exc)}, status=400)
    return Response(payload)

