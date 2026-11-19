from django.urls import path

from apps.dashboard.api.views.overview import (
    DashboardOverviewAPIView,
)
from apps.dashboard.api.views.application import (
    DashboardApplicationListAPIView,
    DashboardApplicationDetailAPIView,
    DashboardApplicationHistoryAPIView,
)
from apps.dashboard.api.views.document import (
    DashboardDocumentListAPIView,
)
from apps.dashboard.api.views.appointment import (
    DashboardAppointmentListAPIView,
)
from apps.dashboard.api.views.profile import (
    DashboardProfileAPIView,
)


urlpatterns = [
    path(
        "overview/",
        DashboardOverviewAPIView.as_view(),
        name="dashboard-overview",
    ),
    path(
        "applications/",
        DashboardApplicationListAPIView.as_view(),
        name="dashboard-applications",
    ),
    path(
        "applications/<str:tracking_code>/",
        DashboardApplicationDetailAPIView.as_view(),
        name="dashboard-application-detail",
    ),
    path(
        "applications/<str:tracking_code>/history/",
        DashboardApplicationHistoryAPIView.as_view(),
        name="dashboard-application-history",
    ),
    path(
        "documents/",
        DashboardDocumentListAPIView.as_view(),
        name="dashboard-documents",
    ),
    path(
        "appointments/",
        DashboardAppointmentListAPIView.as_view(),
        name="dashboard-appointments",
    ),
    path(
        "profile/",
        DashboardProfileAPIView.as_view(),
        name="dashboard-profile",
    ),
]