# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Substations(models.Model):
    raw_id = models.BigAutoField(primary_key=True)
    source_file = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    facility_code = models.TextField(blank=True, null=True)
    facility_name = models.TextField(blank=True, null=True)
    land_location = models.TextField(blank=True, null=True)
    township = models.TextField(blank=True, null=True)
    range = models.TextField(blank=True, null=True)
    meridian = models.TextField(blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)
    capacity_mw = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    unnamed_10 = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'substations'


class WellCasing(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
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
        db_table = 'well_casing'


class WellDates(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    date_well_licensed = models.DateField(blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_dates'


class WellDrilling(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    average_leg_lateral_length_m = models.FloatField(blank=True, null=True)
    bh_temp_degc = models.FloatField(blank=True, null=True)
    casing_flange_elev_m = models.FloatField(blank=True, null=True)
    confid_below_depth_m = models.FloatField(blank=True, null=True)
    confid_release_date = models.DateField(blank=True, null=True)
    crooked_hole_t_f = models.BooleanField(blank=True, null=True)
    date_drlg_completed = models.DateField(blank=True, null=True)
    date_rig_released = models.DateField(blank=True, null=True)
    date_well_spudded = models.DateField(blank=True, null=True)
    deviated_hole_t_f = models.BooleanField(blank=True, null=True)
    drilling_contractor = models.TextField(blank=True, null=True)
    drilling_problems = models.TextField(blank=True, null=True)
    drilling_rig_number = models.TextField(blank=True, null=True)
    drlg_days_spud_cmpl = models.FloatField(blank=True, null=True)
    formation_td = models.TextField(blank=True, null=True)
    ground_elevation_m = models.FloatField(blank=True, null=True)
    horizontal_hole_t_f = models.BooleanField(blank=True, null=True)
    lateral_legs = models.IntegerField(blank=True, null=True)
    lateral_length_m = models.FloatField(blank=True, null=True)
    lateral_start_date = models.DateField(blank=True, null=True)
    leg_lateral_length_m = models.FloatField(blank=True, null=True)
    leg_lateral_start_m = models.TextField(blank=True, null=True)
    logger_ground_elev_m = models.FloatField(blank=True, null=True)
    logger_kb_elev_m = models.FloatField(blank=True, null=True)
    md_all_wells_m = models.FloatField(blank=True, null=True)
    md_deviated_wells_m = models.FloatField(blank=True, null=True)
    multi_lateral_length_m = models.FloatField(blank=True, null=True)
    multi_lateral_license = models.TextField(blank=True, null=True)
    oldest_fm_drilled = models.TextField(blank=True, null=True)
    play = models.TextField(blank=True, null=True)
    plug_back_depth_m = models.FloatField(blank=True, null=True)
    proj_depth = models.FloatField(blank=True, null=True)
    proj_fm_td = models.TextField(blank=True, null=True)
    reference_kb_elev_m = models.FloatField(blank=True, null=True)
    reporting_event = models.TextField(blank=True, null=True)
    tvd_m = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_drilling'


class WellHeader(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    cur_operator_code = models.TextField(blank=True, null=True)
    cur_operator_name = models.TextField(blank=True, null=True)
    lahee_class_code = models.TextField(blank=True, null=True)
    lic_subs_well_obj = models.TextField(blank=True, null=True)
    lic_wa_wid_permit = models.TextField(blank=True, null=True)
    org_operator_name = models.TextField(blank=True, null=True)
    orig_operator_code = models.TextField(blank=True, null=True)
    orig_units_m_api = models.TextField(blank=True, null=True)
    well_name = models.TextField(blank=True, null=True)
    well_pad_id = models.TextField(blank=True, null=True)
    well_type = models.TextField(blank=True, null=True)
    permit_id = models.TextField(db_column='Permit_id', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'well_header'


class WellIdRecordCounts(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    record_count = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_id_record_counts'


class WellLocation(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    bot_hole_e_w_dir = models.TextField(blank=True, null=True)
    bot_hole_easting_nad83 = models.TextField(blank=True, null=True)
    bot_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_n_s_dir = models.TextField(blank=True, null=True)
    bot_hole_northing_nad83 = models.TextField(blank=True, null=True)
    bot_hole_ref_corner = models.TextField(blank=True, null=True)
    bot_hole_zone_nad83 = models.TextField(blank=True, null=True)
    bothole_e_w_distance_m = models.FloatField(blank=True, null=True)
    bothole_n_s_distance_m = models.FloatField(blank=True, null=True)
    govt_surf_loc = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    srfhole_e_w_distance_m = models.FloatField(blank=True, null=True)
    srfhole_n_s_distance_m = models.FloatField(blank=True, null=True)
    surf_hole_e_w_dir = models.TextField(blank=True, null=True)
    surf_hole_easting_nad83 = models.TextField(blank=True, null=True)
    surf_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_n_s_dir = models.TextField(blank=True, null=True)
    surf_hole_northing_nad83 = models.TextField(blank=True, null=True)
    surf_hole_ref_corner = models.TextField(blank=True, null=True)
    surf_hole_zone_nad83 = models.TextField(blank=True, null=True)
    surf_loc = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_location'


class WellLogsAndRemarks(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    casing = models.TextField(blank=True, null=True)
    casing_remarks = models.TextField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    related_land_agreement_s = models.TextField(blank=True, null=True)
    rm = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_logs_and_remarks'


class WellProductionSummary(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    first_12_mo_hrs_on = models.FloatField(blank=True, null=True)
    first_inject_yyyy_mm = models.TextField(blank=True, null=True)
    first_prod_yyyy_mm = models.TextField(blank=True, null=True)
    last_12_mo_hrs_on = models.FloatField(blank=True, null=True)
    last_12_mo_total_boe_bbl = models.FloatField(blank=True, null=True)
    last_12_mo_total_cnd_m3 = models.FloatField(blank=True, null=True)
    last_12_mo_total_gas_e3m3 = models.FloatField(blank=True, null=True)
    last_12_mo_total_oil_m3 = models.FloatField(blank=True, null=True)
    last_12_mo_total_wtr_m3 = models.FloatField(blank=True, null=True)
    last_inject_yyyy_mm = models.TextField(blank=True, null=True)
    last_prod_yyyy_mm = models.TextField(blank=True, null=True)
    most_recent_12_mo_hrs_on = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_boe_bbl = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_cnd_m3 = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_gas_e3m3 = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_oil_m3 = models.FloatField(blank=True, null=True)
    most_recent_12_mo_total_wtr_m3 = models.FloatField(blank=True, null=True)
    on_inject_yyyy_mm_dd = models.DateField(blank=True, null=True)
    on_prod_yyyy_mm_dd = models.DateField(blank=True, null=True)
    prod_inject_frmtn = models.TextField(blank=True, null=True)
    prod_status_abrv = models.TextField(blank=True, null=True)
    prod_status_text = models.TextField(blank=True, null=True)
    total_production_hrs = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_production_summary'


class WellStatus(models.Model):
    base_uwi = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    d13_compliance_status = models.TextField(blank=True, null=True)
    inactive_status_date = models.DateField(blank=True, null=True)
    inactive_well = models.BooleanField(blank=True, null=True)
    industry_reported_suspension_date = models.DateField(blank=True, null=True)
    inspection_date = models.DateField(blank=True, null=True)
    iwcp = models.BooleanField(blank=True, null=True)
    last_reported_downhole_operation = models.TextField(blank=True, null=True)
    next_inspection_due = models.DateField(blank=True, null=True)
    noncompliance_details = models.TextField(blank=True, null=True)
    orphan_abd_status = models.TextField(blank=True, null=True)
    orphan_rec_status = models.TextField(blank=True, null=True)
    owa_cost_area = models.TextField(blank=True, null=True)
    reclamation_certificate = models.TextField(blank=True, null=True)
    reported_risk_class = models.TextField(blank=True, null=True)
    risk_class = models.TextField(blank=True, null=True)
    shut_in_time_mos = models.FloatField(blank=True, null=True)
    shut_in_well = models.BooleanField(blank=True, null=True)
    status_history = models.TextField(blank=True, null=True)
    surface_abandonment_date = models.DateField(blank=True, null=True)
    surface_abandonment_type = models.TextField(blank=True, null=True)
    type_6_well = models.BooleanField(blank=True, null=True)
    well_status_abrv = models.TextField(blank=True, null=True)
    well_status_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'well_status'


class WellfileRawAll(models.Model):
    raw_id = models.BigAutoField(primary_key=True)
    source_file = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    well_status_abrv = models.TextField(blank=True, null=True)
    well_status_text = models.TextField(blank=True, null=True)
    lahee_class_code = models.TextField(blank=True, null=True)
    orig_operator_code = models.TextField(blank=True, null=True)
    org_operator_name = models.TextField(blank=True, null=True)
    cur_operator_code = models.TextField(blank=True, null=True)
    cur_operator_name = models.TextField(blank=True, null=True)
    lic_wa_wid_permit = models.TextField(blank=True, null=True)
    date_well_licensed = models.TextField(blank=True, null=True)
    lic_subs_well_obj = models.TextField(blank=True, null=True)
    date_well_spudded = models.TextField(blank=True, null=True)
    date_drlg_completed = models.TextField(blank=True, null=True)
    date_rig_released = models.TextField(blank=True, null=True)
    drlg_days_spud_cmpl = models.TextField(blank=True, null=True)
    orig_units_m_api = models.TextField(blank=True, null=True)
    reference_kb_elev_m = models.TextField(blank=True, null=True)
    ground_elevation_m = models.TextField(blank=True, null=True)
    logger_kb_elev_m = models.TextField(blank=True, null=True)
    logger_ground_elev_m = models.TextField(blank=True, null=True)
    casing_flange_elev_m = models.TextField(blank=True, null=True)
    md_all_wells_m = models.TextField(blank=True, null=True)
    md_deviated_wells_m = models.TextField(blank=True, null=True)
    tvd_m = models.TextField(blank=True, null=True)
    lateral_length_m = models.TextField(blank=True, null=True)
    leg_lateral_length_m = models.TextField(blank=True, null=True)
    leg_lateral_start_m = models.TextField(blank=True, null=True)
    lateral_start_date = models.TextField(blank=True, null=True)
    multi_lateral_length_m = models.TextField(blank=True, null=True)
    average_leg_lateral_length_m = models.TextField(blank=True, null=True)
    lateral_legs = models.TextField(blank=True, null=True)
    multi_lateral_license = models.TextField(blank=True, null=True)
    reporting_event = models.TextField(blank=True, null=True)
    plug_back_depth_m = models.TextField(blank=True, null=True)
    oldest_fm_drilled = models.TextField(blank=True, null=True)
    formation_td = models.TextField(blank=True, null=True)
    proj_fm_td = models.TextField(blank=True, null=True)
    proj_depth = models.TextField(blank=True, null=True)
    play = models.TextField(blank=True, null=True)
    crooked_hole_t_f = models.TextField(blank=True, null=True)
    deviated_hole_t_f = models.TextField(blank=True, null=True)
    horizontal_hole_t_f = models.TextField(blank=True, null=True)
    confid_below_depth_m = models.TextField(blank=True, null=True)
    confid_release_date = models.TextField(blank=True, null=True)
    update_date = models.TextField(blank=True, null=True)
    well_name = models.TextField(blank=True, null=True)
    well_pad_id = models.TextField(blank=True, null=True)
    drilling_contractor = models.TextField(blank=True, null=True)
    drilling_rig_number = models.TextField(blank=True, null=True)
    surface_abandonment_date = models.TextField(blank=True, null=True)
    surface_abandonment_type = models.TextField(blank=True, null=True)
    shut_in_well = models.TextField(blank=True, null=True)
    shut_in_time_mos = models.TextField(blank=True, null=True)
    inactive_well = models.TextField(blank=True, null=True)
    inactive_status_date = models.TextField(blank=True, null=True)
    industry_reported_suspension_date = models.TextField(blank=True, null=True)
    d13_compliance_status = models.TextField(blank=True, null=True)
    noncompliance_details = models.TextField(blank=True, null=True)
    iwcp = models.TextField(blank=True, null=True)
    inspection_date = models.TextField(blank=True, null=True)
    next_inspection_due = models.TextField(blank=True, null=True)
    well_type = models.TextField(blank=True, null=True)
    last_reported_downhole_operation = models.TextField(blank=True, null=True)
    reported_risk_class = models.TextField(blank=True, null=True)
    risk_class = models.TextField(blank=True, null=True)
    type_6_well = models.TextField(blank=True, null=True)
    reclamation_certificate = models.TextField(blank=True, null=True)
    orphan_abd_status = models.TextField(blank=True, null=True)
    orphan_rec_status = models.TextField(blank=True, null=True)
    owa_cost_area = models.TextField(blank=True, null=True)
    bot_hole_ref_corner = models.TextField(blank=True, null=True)
    bot_hole_n_s_dir = models.TextField(blank=True, null=True)
    bothole_n_s_distance_m = models.TextField(blank=True, null=True)
    bot_hole_e_w_dir = models.TextField(blank=True, null=True)
    bothole_e_w_distance_m = models.TextField(blank=True, null=True)
    surf_loc = models.TextField(blank=True, null=True)
    govt_surf_loc = models.TextField(blank=True, null=True)
    surf_hole_ref_corner = models.TextField(blank=True, null=True)
    surf_hole_n_s_dir = models.TextField(blank=True, null=True)
    srfhole_n_s_distance_m = models.TextField(blank=True, null=True)
    surf_hole_e_w_dir = models.TextField(blank=True, null=True)
    srfhole_e_w_distance_m = models.TextField(blank=True, null=True)
    bot_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_easting_nad83 = models.TextField(blank=True, null=True)
    bot_hole_northing_nad83 = models.TextField(blank=True, null=True)
    bot_hole_zone_nad83 = models.TextField(blank=True, null=True)
    surf_hole_easting_nad83 = models.TextField(blank=True, null=True)
    surf_hole_northing_nad83 = models.TextField(blank=True, null=True)
    surf_hole_zone_nad83 = models.TextField(blank=True, null=True)
    related_land_agreement_s = models.TextField(blank=True, null=True)
    status_history = models.TextField(blank=True, null=True)
    casing = models.TextField(blank=True, null=True)
    casing_remarks = models.TextField(blank=True, null=True)
    surface_casing_depth_m = models.TextField(blank=True, null=True)
    surface_casing_size_mm = models.TextField(blank=True, null=True)
    surface_casing_weight_kg_m = models.TextField(blank=True, null=True)
    surface_casing_grade = models.TextField(blank=True, null=True)
    surface_casing_remarks = models.TextField(blank=True, null=True)
    surface_casing_location = models.TextField(blank=True, null=True)
    surface_casing_latitude = models.TextField(blank=True, null=True)
    surface_casing_longitude = models.TextField(blank=True, null=True)
    production_casing_depth_m = models.TextField(blank=True, null=True)
    production_casing_size_mm = models.TextField(blank=True, null=True)
    production_casing_weight_kg_m = models.TextField(blank=True, null=True)
    production_casing_grade = models.TextField(blank=True, null=True)
    production_casing_remarks = models.TextField(blank=True, null=True)
    production_casing_location = models.TextField(blank=True, null=True)
    production_casing_latitude = models.TextField(blank=True, null=True)
    production_casing_longitude = models.TextField(blank=True, null=True)
    intermediate_casing_depth_m = models.TextField(blank=True, null=True)
    intermediate_casing_size_mm = models.TextField(blank=True, null=True)
    intermediate_casing_weight_kg_m = models.TextField(blank=True, null=True)
    intermediate_casing_grade = models.TextField(blank=True, null=True)
    intermediate_casing_remarks = models.TextField(blank=True, null=True)
    intermediate_casing_location = models.TextField(blank=True, null=True)
    intermediate_casing_latitude = models.TextField(blank=True, null=True)
    intermediate_casing_longitude = models.TextField(blank=True, null=True)
    cas_casing_depth_m = models.TextField(blank=True, null=True)
    cas_casing_size_mm = models.TextField(blank=True, null=True)
    cas_casing_weight_kg_m = models.TextField(blank=True, null=True)
    cas_casing_grade = models.TextField(blank=True, null=True)
    cas_casing_remarks = models.TextField(blank=True, null=True)
    cas_casing_location = models.TextField(blank=True, null=True)
    cas_casing_latitude = models.TextField(blank=True, null=True)
    cas_casing_longitude = models.TextField(blank=True, null=True)
    conductor_casing_depth_m = models.TextField(blank=True, null=True)
    conductor_casing_size_mm = models.TextField(blank=True, null=True)
    conductor_casing_weight_kg_m = models.TextField(blank=True, null=True)
    conductor_casing_grade = models.TextField(blank=True, null=True)
    conductor_casing_remarks = models.TextField(blank=True, null=True)
    conductor_casing_location = models.TextField(blank=True, null=True)
    conductor_casing_latitude = models.TextField(blank=True, null=True)
    conductor_casing_longitude = models.TextField(blank=True, null=True)
    liner_cemented_casing_depth_m = models.TextField(blank=True, null=True)
    liner_cemented_casing_size_mm = models.TextField(blank=True, null=True)
    liner_cemented_casing_weight_kg_m = models.TextField(blank=True, null=True)
    liner_cemented_casing_grade = models.TextField(blank=True, null=True)
    liner_cemented_casing_remarks = models.TextField(blank=True, null=True)
    liner_cemented_casing_location = models.TextField(blank=True, null=True)
    liner_cemented_casing_latitude = models.TextField(blank=True, null=True)
    liner_cemented_casing_longitude = models.TextField(blank=True, null=True)
    liner_casing_depth_m = models.TextField(blank=True, null=True)
    liner_casing_size_mm = models.TextField(blank=True, null=True)
    liner_casing_weight_kg_m = models.TextField(blank=True, null=True)
    liner_casing_grade = models.TextField(blank=True, null=True)
    liner_casing_remarks = models.TextField(blank=True, null=True)
    liner_casing_location = models.TextField(blank=True, null=True)
    liner_casing_latitude = models.TextField(blank=True, null=True)
    liner_casing_longitude = models.TextField(blank=True, null=True)
    surf_prod_casing_depth_m = models.TextField(blank=True, null=True)
    surf_prod_casing_size_mm = models.TextField(blank=True, null=True)
    surf_prod_casing_weight_kg_m = models.TextField(blank=True, null=True)
    surf_prod_casing_grade = models.TextField(blank=True, null=True)
    surf_prod_casing_remarks = models.TextField(blank=True, null=True)
    surf_prod_casing_location = models.TextField(blank=True, null=True)
    surf_prod_casing_latitude = models.TextField(blank=True, null=True)
    surf_prod_casing_longitude = models.TextField(blank=True, null=True)
    tie_back_casing_depth_m = models.TextField(blank=True, null=True)
    tie_back_casing_size_mm = models.TextField(blank=True, null=True)
    tie_back_casing_weight_kg_m = models.TextField(blank=True, null=True)
    tie_back_casing_grade = models.TextField(blank=True, null=True)
    tie_back_casing_remarks = models.TextField(blank=True, null=True)
    tie_back_casing_location = models.TextField(blank=True, null=True)
    tie_back_casing_latitude = models.TextField(blank=True, null=True)
    tie_back_casing_longitude = models.TextField(blank=True, null=True)
    tubular_casing_depth_m = models.TextField(blank=True, null=True)
    tubular_casing_size_mm = models.TextField(blank=True, null=True)
    tubular_casing_weight_kg_m = models.TextField(blank=True, null=True)
    tubular_casing_grade = models.TextField(blank=True, null=True)
    tubular_casing_remarks = models.TextField(blank=True, null=True)
    tubular_casing_location = models.TextField(blank=True, null=True)
    tubular_casing_latitude = models.TextField(blank=True, null=True)
    tubular_casing_longitude = models.TextField(blank=True, null=True)
    no_casing_run_casing_depth_m = models.TextField(blank=True, null=True)
    no_casing_run_casing_size_mm = models.TextField(blank=True, null=True)
    no_casing_run_casing_weight_kg_m = models.TextField(blank=True, null=True)
    no_casing_run_casing_grade = models.TextField(blank=True, null=True)
    no_casing_run_casing_remarks = models.TextField(blank=True, null=True)
    no_casing_run_casing_location = models.TextField(blank=True, null=True)
    no_casing_run_casing_latitude = models.TextField(blank=True, null=True)
    no_casing_run_casing_longitude = models.TextField(blank=True, null=True)
    unknown_casing_depth_m = models.TextField(blank=True, null=True)
    unknown_casing_size_mm = models.TextField(blank=True, null=True)
    unknown_casing_weight_kg_m = models.TextField(blank=True, null=True)
    unknown_casing_grade = models.TextField(blank=True, null=True)
    unknown_casing_remarks = models.TextField(blank=True, null=True)
    unknown_casing_location = models.TextField(blank=True, null=True)
    unknown_casing_latitude = models.TextField(blank=True, null=True)
    unknown_casing_longitude = models.TextField(blank=True, null=True)
    rm = models.TextField(blank=True, null=True)
    bh_temp_degc = models.TextField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    drilling_problems = models.TextField(blank=True, null=True)
    prod_inject_frmtn = models.TextField(blank=True, null=True)
    prod_status_abrv = models.TextField(blank=True, null=True)
    prod_status_text = models.TextField(blank=True, null=True)
    on_prod_yyyy_mm_dd = models.TextField(blank=True, null=True)
    first_prod_yyyy_mm = models.TextField(blank=True, null=True)
    last_prod_yyyy_mm = models.TextField(blank=True, null=True)
    last_12_mo_total_gas_e3m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_oil_m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_cnd_m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_wtr_m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_boe_bbl = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_gas_e3m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_oil_m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_cnd_m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_wtr_m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_boe_bbl = models.TextField(blank=True, null=True)
    on_inject_yyyy_mm_dd = models.TextField(blank=True, null=True)
    first_inject_yyyy_mm = models.TextField(blank=True, null=True)
    last_inject_yyyy_mm = models.TextField(blank=True, null=True)
    total_production_hrs = models.TextField(blank=True, null=True)
    first_12_mo_hrs_on = models.TextField(blank=True, null=True)
    last_12_mo_hrs_on = models.TextField(blank=True, null=True)
    most_recent_12_mo_hrs_on = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    base_uwi = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wellfile_raw_all'


class WellfileRawUnique(models.Model):
    raw_id = models.BigIntegerField(blank=True, null=True)
    source_file = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    well_status_abrv = models.TextField(blank=True, null=True)
    well_status_text = models.TextField(blank=True, null=True)
    lahee_class_code = models.TextField(blank=True, null=True)
    orig_operator_code = models.TextField(blank=True, null=True)
    org_operator_name = models.TextField(blank=True, null=True)
    cur_operator_code = models.TextField(blank=True, null=True)
    cur_operator_name = models.TextField(blank=True, null=True)
    lic_wa_wid_permit = models.TextField(blank=True, null=True)
    date_well_licensed = models.TextField(blank=True, null=True)
    lic_subs_well_obj = models.TextField(blank=True, null=True)
    date_well_spudded = models.TextField(blank=True, null=True)
    date_drlg_completed = models.TextField(blank=True, null=True)
    date_rig_released = models.TextField(blank=True, null=True)
    drlg_days_spud_cmpl = models.TextField(blank=True, null=True)
    orig_units_m_api = models.TextField(blank=True, null=True)
    reference_kb_elev_m = models.TextField(blank=True, null=True)
    ground_elevation_m = models.TextField(blank=True, null=True)
    logger_kb_elev_m = models.TextField(blank=True, null=True)
    logger_ground_elev_m = models.TextField(blank=True, null=True)
    casing_flange_elev_m = models.TextField(blank=True, null=True)
    md_all_wells_m = models.TextField(blank=True, null=True)
    md_deviated_wells_m = models.TextField(blank=True, null=True)
    tvd_m = models.TextField(blank=True, null=True)
    lateral_length_m = models.TextField(blank=True, null=True)
    leg_lateral_length_m = models.TextField(blank=True, null=True)
    leg_lateral_start_m = models.TextField(blank=True, null=True)
    lateral_start_date = models.TextField(blank=True, null=True)
    multi_lateral_length_m = models.TextField(blank=True, null=True)
    average_leg_lateral_length_m = models.TextField(blank=True, null=True)
    lateral_legs = models.TextField(blank=True, null=True)
    multi_lateral_license = models.TextField(blank=True, null=True)
    reporting_event = models.TextField(blank=True, null=True)
    plug_back_depth_m = models.TextField(blank=True, null=True)
    oldest_fm_drilled = models.TextField(blank=True, null=True)
    formation_td = models.TextField(blank=True, null=True)
    proj_fm_td = models.TextField(blank=True, null=True)
    proj_depth = models.TextField(blank=True, null=True)
    play = models.TextField(blank=True, null=True)
    crooked_hole_t_f = models.TextField(blank=True, null=True)
    deviated_hole_t_f = models.TextField(blank=True, null=True)
    horizontal_hole_t_f = models.TextField(blank=True, null=True)
    confid_below_depth_m = models.TextField(blank=True, null=True)
    confid_release_date = models.TextField(blank=True, null=True)
    update_date = models.TextField(blank=True, null=True)
    well_name = models.TextField(blank=True, null=True)
    well_pad_id = models.TextField(blank=True, null=True)
    drilling_contractor = models.TextField(blank=True, null=True)
    drilling_rig_number = models.TextField(blank=True, null=True)
    surface_abandonment_date = models.TextField(blank=True, null=True)
    surface_abandonment_type = models.TextField(blank=True, null=True)
    shut_in_well = models.TextField(blank=True, null=True)
    shut_in_time_mos = models.TextField(blank=True, null=True)
    inactive_well = models.TextField(blank=True, null=True)
    inactive_status_date = models.TextField(blank=True, null=True)
    industry_reported_suspension_date = models.TextField(blank=True, null=True)
    d13_compliance_status = models.TextField(blank=True, null=True)
    noncompliance_details = models.TextField(blank=True, null=True)
    iwcp = models.TextField(blank=True, null=True)
    inspection_date = models.TextField(blank=True, null=True)
    next_inspection_due = models.TextField(blank=True, null=True)
    well_type = models.TextField(blank=True, null=True)
    last_reported_downhole_operation = models.TextField(blank=True, null=True)
    reported_risk_class = models.TextField(blank=True, null=True)
    risk_class = models.TextField(blank=True, null=True)
    type_6_well = models.TextField(blank=True, null=True)
    reclamation_certificate = models.TextField(blank=True, null=True)
    orphan_abd_status = models.TextField(blank=True, null=True)
    orphan_rec_status = models.TextField(blank=True, null=True)
    owa_cost_area = models.TextField(blank=True, null=True)
    bot_hole_ref_corner = models.TextField(blank=True, null=True)
    bot_hole_n_s_dir = models.TextField(blank=True, null=True)
    bothole_n_s_distance_m = models.TextField(blank=True, null=True)
    bot_hole_e_w_dir = models.TextField(blank=True, null=True)
    bothole_e_w_distance_m = models.TextField(blank=True, null=True)
    surf_loc = models.TextField(blank=True, null=True)
    govt_surf_loc = models.TextField(blank=True, null=True)
    surf_hole_ref_corner = models.TextField(blank=True, null=True)
    surf_hole_n_s_dir = models.TextField(blank=True, null=True)
    srfhole_n_s_distance_m = models.TextField(blank=True, null=True)
    surf_hole_e_w_dir = models.TextField(blank=True, null=True)
    srfhole_e_w_distance_m = models.TextField(blank=True, null=True)
    bot_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    bot_hole_easting_nad83 = models.TextField(blank=True, null=True)
    bot_hole_northing_nad83 = models.TextField(blank=True, null=True)
    bot_hole_zone_nad83 = models.TextField(blank=True, null=True)
    surf_hole_easting_nad83 = models.TextField(blank=True, null=True)
    surf_hole_northing_nad83 = models.TextField(blank=True, null=True)
    surf_hole_zone_nad83 = models.TextField(blank=True, null=True)
    related_land_agreement_s = models.TextField(blank=True, null=True)
    status_history = models.TextField(blank=True, null=True)
    casing = models.TextField(blank=True, null=True)
    casing_remarks = models.TextField(blank=True, null=True)
    surface_casing_depth_m = models.TextField(blank=True, null=True)
    surface_casing_size_mm = models.TextField(blank=True, null=True)
    surface_casing_weight_kg_m = models.TextField(blank=True, null=True)
    surface_casing_grade = models.TextField(blank=True, null=True)
    surface_casing_remarks = models.TextField(blank=True, null=True)
    surface_casing_location = models.TextField(blank=True, null=True)
    surface_casing_latitude = models.TextField(blank=True, null=True)
    surface_casing_longitude = models.TextField(blank=True, null=True)
    production_casing_depth_m = models.TextField(blank=True, null=True)
    production_casing_size_mm = models.TextField(blank=True, null=True)
    production_casing_weight_kg_m = models.TextField(blank=True, null=True)
    production_casing_grade = models.TextField(blank=True, null=True)
    production_casing_remarks = models.TextField(blank=True, null=True)
    production_casing_location = models.TextField(blank=True, null=True)
    production_casing_latitude = models.TextField(blank=True, null=True)
    production_casing_longitude = models.TextField(blank=True, null=True)
    intermediate_casing_depth_m = models.TextField(blank=True, null=True)
    intermediate_casing_size_mm = models.TextField(blank=True, null=True)
    intermediate_casing_weight_kg_m = models.TextField(blank=True, null=True)
    intermediate_casing_grade = models.TextField(blank=True, null=True)
    intermediate_casing_remarks = models.TextField(blank=True, null=True)
    intermediate_casing_location = models.TextField(blank=True, null=True)
    intermediate_casing_latitude = models.TextField(blank=True, null=True)
    intermediate_casing_longitude = models.TextField(blank=True, null=True)
    cas_casing_depth_m = models.TextField(blank=True, null=True)
    cas_casing_size_mm = models.TextField(blank=True, null=True)
    cas_casing_weight_kg_m = models.TextField(blank=True, null=True)
    cas_casing_grade = models.TextField(blank=True, null=True)
    cas_casing_remarks = models.TextField(blank=True, null=True)
    cas_casing_location = models.TextField(blank=True, null=True)
    cas_casing_latitude = models.TextField(blank=True, null=True)
    cas_casing_longitude = models.TextField(blank=True, null=True)
    conductor_casing_depth_m = models.TextField(blank=True, null=True)
    conductor_casing_size_mm = models.TextField(blank=True, null=True)
    conductor_casing_weight_kg_m = models.TextField(blank=True, null=True)
    conductor_casing_grade = models.TextField(blank=True, null=True)
    conductor_casing_remarks = models.TextField(blank=True, null=True)
    conductor_casing_location = models.TextField(blank=True, null=True)
    conductor_casing_latitude = models.TextField(blank=True, null=True)
    conductor_casing_longitude = models.TextField(blank=True, null=True)
    liner_cemented_casing_depth_m = models.TextField(blank=True, null=True)
    liner_cemented_casing_size_mm = models.TextField(blank=True, null=True)
    liner_cemented_casing_weight_kg_m = models.TextField(blank=True, null=True)
    liner_cemented_casing_grade = models.TextField(blank=True, null=True)
    liner_cemented_casing_remarks = models.TextField(blank=True, null=True)
    liner_cemented_casing_location = models.TextField(blank=True, null=True)
    liner_cemented_casing_latitude = models.TextField(blank=True, null=True)
    liner_cemented_casing_longitude = models.TextField(blank=True, null=True)
    liner_casing_depth_m = models.TextField(blank=True, null=True)
    liner_casing_size_mm = models.TextField(blank=True, null=True)
    liner_casing_weight_kg_m = models.TextField(blank=True, null=True)
    liner_casing_grade = models.TextField(blank=True, null=True)
    liner_casing_remarks = models.TextField(blank=True, null=True)
    liner_casing_location = models.TextField(blank=True, null=True)
    liner_casing_latitude = models.TextField(blank=True, null=True)
    liner_casing_longitude = models.TextField(blank=True, null=True)
    surf_prod_casing_depth_m = models.TextField(blank=True, null=True)
    surf_prod_casing_size_mm = models.TextField(blank=True, null=True)
    surf_prod_casing_weight_kg_m = models.TextField(blank=True, null=True)
    surf_prod_casing_grade = models.TextField(blank=True, null=True)
    surf_prod_casing_remarks = models.TextField(blank=True, null=True)
    surf_prod_casing_location = models.TextField(blank=True, null=True)
    surf_prod_casing_latitude = models.TextField(blank=True, null=True)
    surf_prod_casing_longitude = models.TextField(blank=True, null=True)
    tie_back_casing_depth_m = models.TextField(blank=True, null=True)
    tie_back_casing_size_mm = models.TextField(blank=True, null=True)
    tie_back_casing_weight_kg_m = models.TextField(blank=True, null=True)
    tie_back_casing_grade = models.TextField(blank=True, null=True)
    tie_back_casing_remarks = models.TextField(blank=True, null=True)
    tie_back_casing_location = models.TextField(blank=True, null=True)
    tie_back_casing_latitude = models.TextField(blank=True, null=True)
    tie_back_casing_longitude = models.TextField(blank=True, null=True)
    tubular_casing_depth_m = models.TextField(blank=True, null=True)
    tubular_casing_size_mm = models.TextField(blank=True, null=True)
    tubular_casing_weight_kg_m = models.TextField(blank=True, null=True)
    tubular_casing_grade = models.TextField(blank=True, null=True)
    tubular_casing_remarks = models.TextField(blank=True, null=True)
    tubular_casing_location = models.TextField(blank=True, null=True)
    tubular_casing_latitude = models.TextField(blank=True, null=True)
    tubular_casing_longitude = models.TextField(blank=True, null=True)
    no_casing_run_casing_depth_m = models.TextField(blank=True, null=True)
    no_casing_run_casing_size_mm = models.TextField(blank=True, null=True)
    no_casing_run_casing_weight_kg_m = models.TextField(blank=True, null=True)
    no_casing_run_casing_grade = models.TextField(blank=True, null=True)
    no_casing_run_casing_remarks = models.TextField(blank=True, null=True)
    no_casing_run_casing_location = models.TextField(blank=True, null=True)
    no_casing_run_casing_latitude = models.TextField(blank=True, null=True)
    no_casing_run_casing_longitude = models.TextField(blank=True, null=True)
    unknown_casing_depth_m = models.TextField(blank=True, null=True)
    unknown_casing_size_mm = models.TextField(blank=True, null=True)
    unknown_casing_weight_kg_m = models.TextField(blank=True, null=True)
    unknown_casing_grade = models.TextField(blank=True, null=True)
    unknown_casing_remarks = models.TextField(blank=True, null=True)
    unknown_casing_location = models.TextField(blank=True, null=True)
    unknown_casing_latitude = models.TextField(blank=True, null=True)
    unknown_casing_longitude = models.TextField(blank=True, null=True)
    rm = models.TextField(blank=True, null=True)
    bh_temp_degc = models.TextField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    drilling_problems = models.TextField(blank=True, null=True)
    prod_inject_frmtn = models.TextField(blank=True, null=True)
    prod_status_abrv = models.TextField(blank=True, null=True)
    prod_status_text = models.TextField(blank=True, null=True)
    on_prod_yyyy_mm_dd = models.TextField(blank=True, null=True)
    first_prod_yyyy_mm = models.TextField(blank=True, null=True)
    last_prod_yyyy_mm = models.TextField(blank=True, null=True)
    last_12_mo_total_gas_e3m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_oil_m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_cnd_m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_wtr_m3 = models.TextField(blank=True, null=True)
    last_12_mo_total_boe_bbl = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_gas_e3m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_oil_m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_cnd_m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_wtr_m3 = models.TextField(blank=True, null=True)
    most_recent_12_mo_total_boe_bbl = models.TextField(blank=True, null=True)
    on_inject_yyyy_mm_dd = models.TextField(blank=True, null=True)
    first_inject_yyyy_mm = models.TextField(blank=True, null=True)
    last_inject_yyyy_mm = models.TextField(blank=True, null=True)
    total_production_hrs = models.TextField(blank=True, null=True)
    first_12_mo_hrs_on = models.TextField(blank=True, null=True)
    last_12_mo_hrs_on = models.TextField(blank=True, null=True)
    most_recent_12_mo_hrs_on = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    base_uwi = models.TextField(blank=True, null=True)
    suffix = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wellfile_raw_unique'


class WellsCasingstring(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80)
    size_mm = models.DecimalField(max_digits=8, decimal_places=2)
    weight_kg_m = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    grade = models.CharField(max_length=80)
    set_depth_m = models.DecimalField(max_digits=10, decimal_places=2)
    cement_top_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    well = models.ForeignKey('WellsWell', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wells_casingstring'


class WellsCompletion(models.Model):
    id = models.BigAutoField(primary_key=True)
    interval_top_m = models.DecimalField(max_digits=10, decimal_places=2)
    interval_bottom_m = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=120)
    fluid_system = models.CharField(max_length=120)
    completed_on = models.DateField(blank=True, null=True)
    well = models.ForeignKey('WellsWell', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wells_completion'


class WellsFormationtop(models.Model):
    id = models.BigAutoField(primary_key=True)
    formation_name = models.CharField(max_length=120)
    top_depth_m = models.DecimalField(max_digits=10, decimal_places=2)
    lithology = models.CharField(max_length=160)
    well = models.ForeignKey('WellsWell', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wells_formationtop'


class WellsProductionsample(models.Model):
    id = models.BigAutoField(primary_key=True)
    production_date = models.DateField()
    oil_m3 = models.DecimalField(max_digits=12, decimal_places=2)
    gas_e3m3 = models.DecimalField(max_digits=12, decimal_places=2)
    water_m3 = models.DecimalField(max_digits=12, decimal_places=2)
    well = models.ForeignKey('WellsWell', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'wells_productionsample'
        unique_together = (('well', 'production_date'),)


class WellsWell(models.Model):
    id = models.BigAutoField(primary_key=True)
    uwi = models.CharField(unique=True, max_length=64)
    name = models.CharField(max_length=160)
    operator = models.CharField(max_length=160)
    field_name = models.CharField(max_length=160)
    status = models.CharField(max_length=32)
    well_type = models.CharField(max_length=32)
    surface_location = models.PointField(geography=True, blank=True, null=True)
    bottomhole_location = models.PointField(geography=True, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    province_state = models.CharField(max_length=80)
    country = models.CharField(max_length=80)
    spud_date = models.DateField(blank=True, null=True)
    rig_release_date = models.DateField(blank=True, null=True)
    true_vertical_depth_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    measured_depth_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'wells_well'


class WellstorAll(models.Model):
    raw_id = models.BigAutoField(primary_key=True)
    source_file = models.TextField(blank=True, null=True)
    import_timestamp = models.TextField(blank=True, null=True)
    user_format_well_id = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    well_status_text = models.TextField(blank=True, null=True)
    date_drlg_completed = models.TextField(blank=True, null=True)
    md_all_wells_m = models.TextField(blank=True, null=True)
    tvd_m = models.TextField(blank=True, null=True)
    crooked_hole_t_f = models.TextField(blank=True, null=True)
    deviated_hole_t_f = models.TextField(blank=True, null=True)
    horizontal_hole_t_f = models.TextField(blank=True, null=True)
    shut_in_well = models.TextField(blank=True, null=True)
    reclamation_certificate = models.TextField(blank=True, null=True)
    orphan_abd_status = models.TextField(blank=True, null=True)
    orphan_rec_status = models.TextField(blank=True, null=True)
    surf_hole_latitude_nad83 = models.TextField(blank=True, null=True)
    surf_hole_longitude_nad83 = models.TextField(blank=True, null=True)
    prod_status_text = models.TextField(blank=True, null=True)
    uwi_base = models.TextField(blank=True, null=True)
    uwi_suffix = models.TextField(blank=True, null=True)
    loc_exc_code = models.TextField(blank=True, null=True)
    legal_subdivisions = models.TextField(blank=True, null=True)
    section = models.TextField(blank=True, null=True)
    township = models.TextField(blank=True, null=True)
    range = models.TextField(blank=True, null=True)
    meridian = models.TextField(blank=True, null=True)
    deepest_casing_depth = models.TextField(blank=True, null=True)
    deepest_casing_size = models.TextField(blank=True, null=True)
    deepest_casing_grade = models.TextField(blank=True, null=True)
    deepest_casing_weight = models.TextField(blank=True, null=True)
    max_casing_volume_m3 = models.TextField(blank=True, null=True)
    deepest_casing_id = models.TextField(blank=True, null=True)
    casing_burst_rating_psi = models.TextField(blank=True, null=True)
    idle_well_flag = models.TextField(blank=True, null=True)
    topdepthmd = models.TextField(blank=True, null=True)
    depth_for_available_volume = models.TextField(blank=True, null=True)
    available_wellbore_volume_m3 = models.TextField(blank=True, null=True)
    normalized_wellstor_volume_m3 = models.TextField(blank=True, null=True)
    orphan = models.TextField(blank=True, null=True)
    date_well_licensed = models.TextField(blank=True, null=True)
    date_rig_released = models.TextField(blank=True, null=True)
    md_deviated_wells_m = models.TextField(blank=True, null=True)
    lateral_length_m = models.TextField(blank=True, null=True)
    preffix = models.TextField(blank=True, null=True)
    quarter = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    block = models.TextField(blank=True, null=True)
    series = models.TextField(blank=True, null=True)
    sheet = models.TextField(blank=True, null=True)
    casing_dict_combined = models.TextField(blank=True, null=True)
    deepest_casing_type = models.TextField(blank=True, null=True)
    liner_start_m = models.TextField(blank=True, null=True)
    liner_end_m = models.TextField(blank=True, null=True)
    grade_value = models.TextField(blank=True, null=True)
    wellstor_flag = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wellstor_all'
