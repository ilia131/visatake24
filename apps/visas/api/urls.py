from django.urls import path

from apps.visas.api.views.country import CountryListAPIView

from apps.visas.api.views.application import (
    VisaApplicationListCreateAPIView,
    VisaApplicationDetailAPIView,
    VisaApplicationStatusUpdateAPIView,
    
)
from apps.visas.api.views.history import VisaApplicationHistoryAPIView
from apps.visas.api.views.document import (
    VisaApplicationDocumentListCreateAPIView,
)
from apps.visas.api.views.document_download import (
    VisaApplicationDocumentDownloadAPIView,
)
from apps.visas.api.views.history import VisaApplicationHistoryAPIView

urlpatterns = [

    path(
        "countries/",
        CountryListAPIView.as_view(),
        name="country-list",
    ),

    path(
        "applications/",
        VisaApplicationListCreateAPIView.as_view(),
        name="application-list-create",
    ),
    path(
    "applications/<str:tracking_code>/history/",
    VisaApplicationHistoryAPIView.as_view(),
    name="application-history",
),

    path(
        "applications/<str:tracking_code>/",
        VisaApplicationDetailAPIView.as_view(),
        name="application-detail",
    ),
    path(
    "applications/<str:tracking_code>/status/",
    VisaApplicationStatusUpdateAPIView.as_view(),
    name="visa-application-status-update",
),
    path(
    "applications/<str:tracking_code>/history/",
    VisaApplicationHistoryAPIView.as_view(),
    name="visa-application-history",
),
    path(
    "applications/<str:tracking_code>/documents/",
    VisaApplicationDocumentListCreateAPIView.as_view(),
    name="application-documents",
),
path(
    "documents/<int:document_id>/download/",
    VisaApplicationDocumentDownloadAPIView.as_view(),
    name="visa-document-download",
), path(
        "<int:application_id>/history/",
        VisaApplicationHistoryAPIView.as_view(),
        name="visa-application-history",
    ),

]