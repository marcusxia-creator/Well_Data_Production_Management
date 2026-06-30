from django.urls import path

from .views import databases, delete_data_table, query_table


urlpatterns = [
    path("databases/", databases, name="data-browser-databases"),
    path("query/", query_table, name="data-browser-query"),
    path("tables/", delete_data_table, name="data-browser-delete-table"),
]
