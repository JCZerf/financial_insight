from django.urls import path

from api.views import AdminIngestionRunView, FundDetailView, FundListView, InitialDashboardView

urlpatterns = [
    path("admin/ingestion/run/", AdminIngestionRunView.as_view(), name="admin-ingestion-run"),
    path("dashboard/initial/", InitialDashboardView.as_view(), name="dashboard-initial"),
    path("funds/", FundListView.as_view(), name="fund-list"),
    path("funds/<str:ticker>/", FundDetailView.as_view(), name="fund-detail"),
]
