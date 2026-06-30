from django.contrib import admin

from .models import (
    WellCasing,
    WellDrilling,
    WellHeader,
    WellLocation,
    WellProductionSummary,
    WellStatus,
    WellstorAll,
)


@admin.register(WellHeader)
class WellHeaderAdmin(admin.ModelAdmin):
    list_display = ("base_uwi", "user_format_well_id", "well_name", "area")
    list_filter = ("area",)
    search_fields = ("base_uwi", "user_format_well_id", "well_name")
    readonly_fields = [field.name for field in WellHeader._meta.fields]


@admin.register(WellLocation)
class WellLocationAdmin(admin.ModelAdmin):
    list_display = ("base_uwi", "latitude", "longitude", "surf_loc", "govt_surf_loc")
    search_fields = ("base_uwi__base_uwi", "user_format_well_id", "surf_loc", "govt_surf_loc")
    readonly_fields = [field.name for field in WellLocation._meta.fields]


@admin.register(WellStatus)
class WellStatusAdmin(admin.ModelAdmin):
    list_display = ("base_uwi", "well_status_text", "well_status_abrv", "well_type", "cur_operator_name")
    list_filter = ("well_status_text", "well_type", "inactive_well", "shut_in_well")
    search_fields = ("base_uwi__base_uwi", "user_format_well_id", "well_status_text", "cur_operator_name")
    readonly_fields = [field.name for field in WellStatus._meta.fields]


@admin.register(WellDrilling)
class WellDrillingAdmin(admin.ModelAdmin):
    list_display = ("base_uwi", "date_well_spudded", "date_rig_released", "md_all_wells_m", "tvd_m")
    search_fields = ("base_uwi__base_uwi", "user_format_well_id", "drilling_contractor")
    readonly_fields = [field.name for field in WellDrilling._meta.fields]


@admin.register(WellCasing)
class WellCasingAdmin(admin.ModelAdmin):
    list_display = ("base_uwi", "casing_type", "casing_size_mm", "casing_depth_m", "casing_grade")
    list_filter = ("casing_type", "casing_grade")
    search_fields = ("base_uwi__base_uwi", "user_format_well_id", "casing_type", "casing_grade")
    readonly_fields = [field.name for field in WellCasing._meta.fields]


@admin.register(WellProductionSummary)
class WellProductionSummaryAdmin(admin.ModelAdmin):
    list_display = (
        "base_uwi",
        "prod_status_text",
        "most_recent_12_mo_total_oil_m3",
        "most_recent_12_mo_total_gas_e3m3",
        "most_recent_12_mo_total_wtr_m3",
    )
    list_filter = ("prod_status_text",)
    search_fields = ("base_uwi__base_uwi", "user_format_well_id", "prod_status_text")
    readonly_fields = [field.name for field in WellProductionSummary._meta.fields]


@admin.register(WellstorAll)
class WellstorAllAdmin(admin.ModelAdmin):
    list_display = ("base_uwi", "user_format_well_id", "well_status_text", "wellstor_flag", "normalized_wellstor_volume_m3")
    list_filter = ("wellstor_flag", "orphan", "well_status_text")
    search_fields = ("base_uwi", "user_format_well_id")
    readonly_fields = [field.name for field in WellstorAll._meta.fields]
