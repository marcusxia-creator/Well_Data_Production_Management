from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from config.auth_views import auth_status, login_account, logout_account, setup_account

from apps.wells.views import (
    WellViewSet,
    actual_well_statuses,
    current_operators,
    dashboard_data_sources,
    dashboard_source_options,
    dashboard_source_wells,
    production_injection_formations,
    well_statuses,
    well_types,
)

router = DefaultRouter()
router.register("wells", WellViewSet, basename="well")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/status/", auth_status, name="auth-status"),
    path("api/auth/setup/", setup_account, name="auth-setup"),
    path("api/auth/login/", login_account, name="auth-login"),
    path("api/auth/logout/", logout_account, name="auth-logout"),
    path("api/", include(router.urls)),
    path("api/imports/", include("apps.data_imports.urls")),
    path("api/data-browser/", include("apps.data_browser.urls")),
    path("api/well-statuses/", well_statuses, name="well-statuses"),
    path("api/actual-well-statuses/", actual_well_statuses, name="actual-well-statuses"),
    path("api/well-types/", well_types, name="well-types"),
    path("api/current-operators/", current_operators, name="current-operators"),
    path("api/dashboard-data-sources/", dashboard_data_sources, name="dashboard-data-sources"),
    path("api/dashboard-source-options/", dashboard_source_options, name="dashboard-source-options"),
    path("api/dashboard-source-wells/", dashboard_source_wells, name="dashboard-source-wells"),
    path("api/production-injection-formations/", production_injection_formations, name="production-injection-formations"),
]


