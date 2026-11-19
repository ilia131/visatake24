from django.urls import path
from apps.appointments.api.views.availability import (
    AvailabilityListAPIView,
    AvailabilityDetailAPIView,
)
from apps.appointments.api.views.availability_admin import (
    AvailabilityAdminListCreateAPIView,
    AvailabilityAdminDetailAPIView,
)
from apps.appointments.api.views.appointment import (
    AppointmentListCreateAPIView,
    AppointmentCancelAPIView,
    AppointmentDetailAPIView,
    ConsultantAppointmentDetailAPIView,
    ConsultantAppointmentListAPIView,
    ConsultantApproveAPIView,
    ConsultantCompleteAPIView,
    ConsultantRejectAPIView,
    PaymentApproveAPIView,
    PaymentDetailAPIView,
    PaymentListAPIView,
    PaymentRejectAPIView,
    ReceiptDownloadAPIView,
    ReceiptUploadAPIView,
)
urlpatterns = [
    path("availability/", AvailabilityListAPIView.as_view()),
    path("availability/<int:pk>/", AvailabilityDetailAPIView.as_view()),
    path(
        "availability/manage/",
        AvailabilityAdminListCreateAPIView.as_view(),
    ),
    path(
        "availability/manage/<int:pk>/",
        AvailabilityAdminDetailAPIView.as_view(),
    ),
    path("consultant/", ConsultantAppointmentListAPIView.as_view()),
    path("consultant/<int:pk>/", ConsultantAppointmentDetailAPIView.as_view()),
    path("consultant/<int:pk>/approve/", ConsultantApproveAPIView.as_view()),
    path("consultant/<int:pk>/reject/", ConsultantRejectAPIView.as_view()),
    path("consultant/<int:pk>/complete/", ConsultantCompleteAPIView.as_view()),
    path("admin/payments/", PaymentListAPIView.as_view()),
    path("admin/payments/<int:pk>/", PaymentDetailAPIView.as_view()),
    path("admin/payments/<int:pk>/approve/", PaymentApproveAPIView.as_view()),
    path("admin/payments/<int:pk>/reject/", PaymentRejectAPIView.as_view()),
    path("<int:pk>/", AppointmentDetailAPIView.as_view(), name="appointment-detail"),
    path("<int:pk>/payment-receipt/", ReceiptUploadAPIView.as_view()),
    path("<int:pk>/payment-receipt/download/", ReceiptDownloadAPIView.as_view(), name="appointment-receipt-download"),
    path("", AppointmentListCreateAPIView.as_view(), name="appointment-list-create"),
    path("<int:pk>/cancel/", AppointmentCancelAPIView.as_view(), name="appointment-cancel"),
]