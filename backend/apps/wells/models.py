from django.db import models


class WellHeader(models.Model):
    base_uwi = models.TextField(primary_key=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    well_name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "well_header"
        ordering = ["base_uwi", "-suffix", "-raw_id"]

    def __str__(self):
        return f"{self.base_uwi} - {self.well_name or self.user_format_well_id or ''}".strip()


class WellLocation(models.Model):
    raw_id = models.BigIntegerField(primary_key=True)
    base_uwi = models.ForeignKey(
        WellHeader,
        models.DO_NOTHING,
        db_column="base_uwi",
        to_field="base_uwi",
        related_name="locations",
        db_constraint=False,
        blank=True,
        null=True,
    )
    import_timestamp = models.TextField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    bot_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    govt_surf_loc = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    surf_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    surf_loc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "well_location"
        ordering = ["base_uwi", "-suffix", "-raw_id"]

    def __str__(self):
        return f"{self.base_uwi_id} location"


class WellStatus(models.Model):
    raw_id = models.BigIntegerField(primary_key=True)
    base_uwi = models.ForeignKey(
        WellHeader,
        models.DO_NOTHING,
        db_column="base_uwi",
        to_field="base_uwi",
        related_name="statuses",
        db_constraint=False,
        blank=True,
        null=True,
    )
    import_timestamp = models.TextField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    cur_operator_code = models.TextField(blank=True, null=True)
    cur_operator_name = models.TextField(blank=True, null=True)
    lahee_class_code = models.TextField(blank=True, null=True)
    lic_subs_well_obj = models.TextField(blank=True, null=True)
    lic_wa_wid_permit = models.TextField(blank=True, null=True)
    org_operator_name = models.TextField(blank=True, null=True)
    orig_operator_code = models.TextField(blank=True, null=True)
    orig_units_m_api = models.TextField(blank=True, null=True)
    well_pad_id = models.TextField(blank=True, null=True)
    well_type = models.TextField(blank=True, null=True)
    permit_id = models.TextField(db_column="Permit_id", blank=True, null=True)
    inactive_well = models.BooleanField(blank=True, null=True)
    shut_in_well = models.BooleanField(blank=True, null=True)
    well_status_abrv = models.TextField(blank=True, null=True)
    well_status_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "well_status"
        ordering = ["base_uwi", "-suffix", "-raw_id"]

    def __str__(self):
        return f"{self.base_uwi_id} status"


class WellStatusCategory(models.Model):
    base_uwi = models.TextField(primary_key=True)
    status_category = models.CharField(max_length=32, db_index=True)
    actual_status_text = models.TextField(blank=True, null=True, db_index=True)
    last_production_date = models.DateField(blank=True, null=True)
    last_injection_date = models.DateField(blank=True, null=True)
    refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "well_status_category"
        indexes = [
            models.Index(fields=["status_category", "actual_status_text"]),
        ]

    def __str__(self):
        return f"{self.base_uwi} {self.status_category}"


class WellDrilling(models.Model):
    raw_id = models.BigIntegerField(primary_key=True)
    base_uwi = models.ForeignKey(
        WellHeader,
        models.DO_NOTHING,
        db_column="base_uwi",
        to_field="base_uwi",
        related_name="drilling_records",
        db_constraint=False,
        blank=True,
        null=True,
    )
    import_timestamp = models.TextField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    date_drlg_completed = models.DateField(blank=True, null=True)
    date_rig_released = models.DateField(blank=True, null=True)
    date_well_spudded = models.DateField(blank=True, null=True)
    drilling_contractor = models.TextField(blank=True, null=True)
    drilling_rig_number = models.TextField(blank=True, null=True)
    md_all_wells_m = models.FloatField(blank=True, null=True)
    md_deviated_wells_m = models.FloatField(blank=True, null=True)
    tvd_m = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "well_drilling"
        ordering = ["base_uwi", "-suffix", "-raw_id"]

    def __str__(self):
        return f"{self.base_uwi_id} drilling"


class WellCasing(models.Model):
    raw_id = models.BigIntegerField(primary_key=True)
    base_uwi = models.ForeignKey(
        WellHeader,
        models.DO_NOTHING,
        db_column="base_uwi",
        to_field="base_uwi",
        related_name="casing_records",
        db_constraint=False,
        blank=True,
        null=True,
    )
    import_timestamp = models.TextField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    casing_depth_m = models.FloatField(blank=True, null=True)
    casing_grade = models.TextField(blank=True, null=True)
    casing_latitude = models.FloatField(blank=True, null=True)
    casing_location = models.TextField(blank=True, null=True)
    casing_longitude = models.FloatField(blank=True, null=True)
    casing_remarks = models.TextField(blank=True, null=True)
    casing_size_mm = models.FloatField(blank=True, null=True)
    casing_weight_kg_m = models.FloatField(blank=True, null=True)
    casing_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "well_casing"
        ordering = ["base_uwi", "-suffix", "-raw_id"]

    def __str__(self):
        return f"{self.base_uwi_id} {self.casing_type or 'casing'}"


class WellProductionSummary(models.Model):
    raw_id = models.BigIntegerField(primary_key=True)
    base_uwi = models.ForeignKey(
        WellHeader,
        models.DO_NOTHING,
        db_column="base_uwi",
        to_field="base_uwi",
        related_name="production_summaries",
        db_constraint=False,
        blank=True,
        null=True,
    )
    import_timestamp = models.TextField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    prod_status_abrv = models.TextField(blank=True, null=True)
    prod_status_text = models.TextField(blank=True, null=True)
    prod_inject_frmtn = models.TextField(blank=True, null=True)
    on_inject_yyyy_mm_dd = models.DateField(blank=True, null=True)
    on_prod_yyyy_mm_dd = models.DateField(blank=True, null=True)
    first_inject_yyyy_mm = models.TextField(blank=True, null=True)
    first_prod_yyyy_mm = models.TextField(blank=True, null=True)
    last_inject_yyyy_mm = models.TextField(blank=True, null=True)
    last_prod_yyyy_mm = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_gas_e3m3 = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_oil_m3 = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_wtr_m3 = models.FloatField(blank=True, null=True)
    total_production_hrs = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "well_production_summary"
        ordering = ["base_uwi", "-suffix", "-raw_id"]

    def __str__(self):
        return f"{self.base_uwi_id} production summary"


class WellProductionFormation(models.Model):
    base_uwi = models.TextField(db_index=True)
    formation = models.TextField(db_index=True)
    source_value = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "well_production_formation"
        unique_together = ["base_uwi", "formation"]
        indexes = [
            models.Index(fields=["formation", "base_uwi"]),
        ]

    def __str__(self):
        return f"{self.base_uwi} {self.formation}"


class WellCurrentOperator(models.Model):
    base_uwi = models.TextField(primary_key=True)
    operator_name = models.TextField(db_index=True)
    suffix = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    refreshed_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "well_current_operator"
        indexes = [
            models.Index(fields=["operator_name", "base_uwi"], name="wells_well__operato_9176c2_idx"),
        ]

    def __str__(self):
        return f"{self.base_uwi} {self.operator_name}"


class WellstorAll(models.Model):
    raw_id = models.BigAutoField(primary_key=True)
    source_file = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    well_status_text = models.TextField(blank=True, null=True)
    prod_status_text = models.TextField(blank=True, null=True)
    surf_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    base_uwi = models.TextField(db_column="uwi_base", blank=True, null=True)
    uwi_suffix = models.TextField(blank=True, null=True)
    deepest_casing_depth = models.TextField(blank=True, null=True)
    deepest_casing_size = models.TextField(blank=True, null=True)
    deepest_casing_grade = models.TextField(blank=True, null=True)
    deepest_casing_weight = models.TextField(blank=True, null=True)
    max_casing_volume_m3 = models.TextField(blank=True, null=True)
    available_wellbore_volume_m3 = models.TextField(blank=True, null=True)
    normalized_wellstor_volume_m3 = models.TextField(blank=True, null=True)
    orphan = models.TextField(blank=True, null=True)
    wellstor_flag = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "wellstor_all"

    def __str__(self):
        return f"{self.base_uwi or self.user_format_well_id} WellStor"


Well = WellHeader
