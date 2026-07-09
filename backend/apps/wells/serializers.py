from rest_framework import serializers

from .models import WellCasing, WellHeader, WellProductionSummary
from .status_rules import categorize_status, latest_activity_date


def parse_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class WellCasingSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="casing_type", read_only=True)
    size_mm = serializers.FloatField(source="casing_size_mm", read_only=True)
    weight_kg_m = serializers.FloatField(source="casing_weight_kg_m", read_only=True)
    grade = serializers.CharField(source="casing_grade", read_only=True)
    set_depth_m = serializers.FloatField(source="casing_depth_m", read_only=True)
    cement_top_m = serializers.SerializerMethodField()

    class Meta:
        model = WellCasing
        fields = ["raw_id", "name", "size_mm", "weight_kg_m", "grade", "set_depth_m", "cement_top_m"]

    def get_cement_top_m(self, obj):
        return None


class WellProductionSummarySerializer(serializers.ModelSerializer):
    production_date = serializers.SerializerMethodField()
    oil_m3 = serializers.FloatField(source="most_recent_12_mo_total_oil_m3", read_only=True)
    gas_e3m3 = serializers.FloatField(source="most_recent_12_mo_total_gas_e3m3", read_only=True)
    water_m3 = serializers.FloatField(source="most_recent_12_mo_total_wtr_m3", read_only=True)

    class Meta:
        model = WellProductionSummary
        fields = ["raw_id", "production_date", "oil_m3", "gas_e3m3", "water_m3"]

    def get_production_date(self, obj):
        return latest_activity_date(obj)


class WellSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="base_uwi", read_only=True)
    uwi = serializers.CharField(source="base_uwi", read_only=True)
    name = serializers.CharField(source="well_name", read_only=True)
    operator = serializers.SerializerMethodField()
    well_type = serializers.SerializerMethodField()
    field_name = serializers.CharField(source="area", read_only=True)
    status = serializers.SerializerMethodField()
    actual_status_text = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    province_state = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    spud_date = serializers.SerializerMethodField()
    rig_release_date = serializers.SerializerMethodField()
    true_vertical_depth_m = serializers.SerializerMethodField()
    measured_depth_m = serializers.SerializerMethodField()
    casing_strings = WellCasingSerializer(source="casing_records", many=True, read_only=True)
    completions = serializers.SerializerMethodField()
    formation_tops = serializers.SerializerMethodField()
    production_samples = WellProductionSummarySerializer(source="production_summaries", many=True, read_only=True)
    cumulative_oil_volume = serializers.SerializerMethodField()
    cumulative_gas_volume = serializers.SerializerMethodField()
    cumulative_fluid_volume = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = WellHeader
        fields = [
            "id",
            "uwi",
            "name",
            "operator",
            "field_name",
            "status",
            "actual_status_text",
            "well_type",
            "latitude",
            "longitude",
            "province_state",
            "country",
            "spud_date",
            "rig_release_date",
            "true_vertical_depth_m",
            "measured_depth_m",
            "casing_strings",
            "completions",
            "formation_tops",
            "production_samples",
            "cumulative_oil_volume",
            "cumulative_gas_volume",
            "cumulative_fluid_volume",
            "created_at",
            "updated_at",
        ]

    def _first_related(self, obj, related_name):
        related = getattr(obj, related_name).all()
        return related[0] if related else None

    def get_operator(self, obj):
        status = self._first_related(obj, "statuses")
        return getattr(obj, "operator_value", None) or (status.cur_operator_name if status else None)

    def get_well_type(self, obj):
        status = self._first_related(obj, "statuses")
        return getattr(obj, "well_type_value", None) or (status.well_type if status else None)
    def get_status(self, obj):
        if getattr(obj, "status_category_value", None):
            return obj.status_category_value
        status = self._first_related(obj, "statuses")
        production = self._first_related(obj, "production_summaries")
        if status and status.well_status_abrv:
            return status.well_status_abrv
        status_text = status.well_status_text if status else None
        return categorize_status(status_text, production)

    def get_actual_status_text(self, obj):
        if getattr(obj, "actual_status_text_value", None):
            return obj.actual_status_text_value
        status = self._first_related(obj, "statuses")
        if status and status.well_status_text:
            return status.well_status_text
        return "Unknown"

    def get_latitude(self, obj):
        location = self._first_related(obj, "locations")
        if not location:
            return None
        return location.latitude or parse_float(location.surf_hole_latitude_nad83)

    def get_longitude(self, obj):
        location = self._first_related(obj, "locations")
        if not location:
            return None
        return location.longitude or parse_float(location.surf_hole_longitude_nad83)

    def get_province_state(self, obj):
        return "Alberta"

    def get_country(self, obj):
        return "Canada"

    def get_spud_date(self, obj):
        drilling = self._first_related(obj, "drilling_records")
        return drilling.date_well_spudded if drilling else None

    def get_rig_release_date(self, obj):
        drilling = self._first_related(obj, "drilling_records")
        return drilling.date_rig_released if drilling else None

    def get_true_vertical_depth_m(self, obj):
        drilling = self._first_related(obj, "drilling_records")
        return drilling.tvd_m if drilling else None

    def get_measured_depth_m(self, obj):
        drilling = self._first_related(obj, "drilling_records")
        return drilling.md_all_wells_m if drilling else None

    def get_cumulative_oil_volume(self, obj):
        return parse_float(getattr(obj, "cumulative_oil_volume_value", None))

    def get_cumulative_gas_volume(self, obj):
        return parse_float(getattr(obj, "cumulative_gas_volume_value", None))
    def get_cumulative_fluid_volume(self, obj):
        return parse_float(getattr(obj, "cumulative_fluid_volume_value", None))

    def get_completions(self, obj):
        return []

    def get_formation_tops(self, obj):
        return []

    def get_created_at(self, obj):
        return obj.import_timestamp

    def get_updated_at(self, obj):
        return obj.import_timestamp


