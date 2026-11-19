from django.http import FileResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiRequest, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.appointments.api.permissions import (
    IsAdminPaymentReviewer, IsAppointmentOwner, IsAssignedConsultant, can_review_payment,
)
from apps.appointments.api.serializers.appointment import (
    AppointmentCreateSerializer, AppointmentFilterSerializer, AppointmentReviewSerializer,
    AppointmentSerializer, ConsultantRejectSerializer, PaymentRejectSerializer,
    ReceiptUploadSerializer,
)
from apps.appointments.models import Appointment
from apps.appointments.selectors.appointments import (
    appointment_details, get_consultant_appointments, get_payment_appointments,
    get_user_appointments,
)
from apps.appointments.services.booking import book_appointment, cancel_appointment, change_appointment


AUTH_ERRORS = {
    401: OpenApiResponse(description="احراز هویت الزامی است."),
    403: OpenApiResponse(description="مجوز لازم وجود ندارد یا CSRF معتبر نیست."),
}
NOT_FOUND = {404: OpenApiResponse(description="رزرو یا فایل قابل دسترسی نیست.")}
INVALID = {400: OpenApiResponse(description="ورودی، وضعیت رزرو یا زمان انتخاب‌شده معتبر نیست.")}


class OwnerAppointmentsMixin:
    queryset = Appointment.objects.none()
    permission_classes = [IsAppointmentOwner]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return get_user_appointments(user=self.request.user)


@extend_schema_view(
    get=extend_schema(description="فهرست رزروهای کاربر جاری.", responses={200: AppointmentSerializer(many=True), **AUTH_ERRORS}),
    post=extend_schema(
        description="مالک درخواست یک زمان آزاد را رزرو می‌کند.",
        request=AppointmentCreateSerializer,
        responses={201: AppointmentSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
    ),
)
class AppointmentListCreateAPIView(OwnerAppointmentsMixin, generics.ListCreateAPIView):
    def create(self, request, *args, **kwargs):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = book_appointment(user=request.user, **serializer.validated_data)
        return Response(self.get_serializer(appointment).data, status=status.HTTP_201_CREATED)


@extend_schema_view(get=extend_schema(
    description="جزئیات برای مالک رزرو.", responses={200: AppointmentSerializer, **AUTH_ERRORS, **NOT_FOUND},
))
class AppointmentDetailAPIView(OwnerAppointmentsMixin, generics.RetrieveAPIView):
    pass


class AppointmentCancelAPIView(OwnerAppointmentsMixin, generics.GenericAPIView):
    @extend_schema(
        request=None, description="لغو رزرو توسط مالک، مطابق قواعد لغو پروژه.",
        responses={200: AppointmentSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
    )
    def post(self, request, pk):
        appointment = cancel_appointment(appointment_id=pk, user=request.user)
        return Response(self.get_serializer(appointment).data)


class AppointmentPagePagination(PageNumberPagination):
    page_size = 20


class ConsultantAppointmentsMixin:
    queryset = Appointment.objects.none()
    permission_classes = [IsAssignedConsultant]
    serializer_class = AppointmentReviewSerializer

    def get_queryset(self):
        return get_consultant_appointments(user=self.request.user)


@extend_schema_view(get=extend_schema(
    description="فهرست رزروهای مشاور جاری.",
    parameters=[AppointmentFilterSerializer],
    responses={200: AppointmentReviewSerializer(many=True), **AUTH_ERRORS, **NOT_FOUND, **INVALID},
))
class ConsultantAppointmentListAPIView(ConsultantAppointmentsMixin, generics.ListAPIView):
    pagination_class = AppointmentPagePagination

    def get_queryset(self):
        filters = AppointmentFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        criteria = filters.validated_data.copy()
        if "date" in criteria:
            criteria["availability__start_at__date"] = criteria.pop("date")
        return super().get_queryset().filter(**criteria)


@extend_schema_view(get=extend_schema(
    description="جزئیات برای مشاور همین رزرو.",
    responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND},
))
class ConsultantAppointmentDetailAPIView(ConsultantAppointmentsMixin, generics.RetrieveAPIView):
    pass


class PaymentAppointmentsMixin:
    permission_classes = [IsAdminPaymentReviewer]
    serializer_class = AppointmentReviewSerializer

    def get_queryset(self):
        return get_payment_appointments()


@extend_schema_view(get=extend_schema(
    description="صف رسیدهای در انتظار بررسی برای مدیر یا دارنده مجوز بررسی پرداخت.",
    responses={200: AppointmentReviewSerializer(many=True), **AUTH_ERRORS, **NOT_FOUND},
))
class PaymentListAPIView(PaymentAppointmentsMixin, generics.ListAPIView):
    pagination_class = AppointmentPagePagination

    def get_queryset(self):
        return super().get_queryset().filter(status=Appointment.Status.PAYMENT_SUBMITTED)


@extend_schema_view(get=extend_schema(
    description="جزئیات پرداخت و لینک دانلود خصوصی برای بررسی‌کننده.",
    responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND},
))
class PaymentDetailAPIView(PaymentAppointmentsMixin, generics.RetrieveAPIView):
    pass


class AppointmentActionAPIView(generics.GenericAPIView):
    action = None
    input_serializer = None
    note_field = None

    def post(self, request, pk):
        self.get_object()
        data = {}
        if self.input_serializer:
            serializer = self.input_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
        appointment = change_appointment(
            appointment_id=pk, actor=request.user, action=self.action,
            note=data.get(self.note_field, ""), receipt=data.get("payment_receipt"),
        )
        return Response(self.get_serializer(appointment).data)


@extend_schema_view(post=extend_schema(
    description="ارسال یا جایگزینی رسید توسط مالک. فرمت JPEG، PNG یا PDF تا ۵ مگابایت.",
    request={"multipart/form-data": OpenApiRequest(
        request={
            "type": "object", "required": ["payment_receipt"],
            "properties": {"payment_receipt": {"type": "string", "format": "binary"}},
        },
        encoding={"payment_receipt": {"contentType": "image/jpeg, image/png, application/pdf"}},
    )},
    responses={200: AppointmentSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID,
               415: OpenApiResponse(description="نوع بدنه پشتیبانی نمی‌شود.")},
))
class ReceiptUploadAPIView(OwnerAppointmentsMixin, AppointmentActionAPIView):
    action = "submit_receipt"
    input_serializer = ReceiptUploadSerializer
    parser_classes = [MultiPartParser, FormParser]


@extend_schema_view(post=extend_schema(
    description="تأیید درخواست در انتظار توسط مشاور تعیین‌شده و فعال شدن اطلاعات پرداخت برای مالک.",
    request=None, responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
))
class ConsultantApproveAPIView(ConsultantAppointmentsMixin, AppointmentActionAPIView):
    action = "consultant_approve"


@extend_schema_view(post=extend_schema(
    description="رد درخواست در انتظار توسط مشاور تعیین‌شده و آزاد شدن زمان.",
    request=ConsultantRejectSerializer,
    responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
))
class ConsultantRejectAPIView(ConsultantAppointmentsMixin, AppointmentActionAPIView):
    action = "consultant_reject"
    input_serializer = ConsultantRejectSerializer
    note_field = "rejection_reason"


@extend_schema_view(post=extend_schema(
    description="ثبت پایان جلسه توسط مشاور تعیین‌شده، پس از پایان زمان جلسه قطعی.",
    request=None, responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
))
class ConsultantCompleteAPIView(ConsultantAppointmentsMixin, AppointmentActionAPIView):
    action = "complete"


@extend_schema_view(post=extend_schema(
    description="تأیید رسید در انتظار بررسی و قطعی کردن رزرو توسط بررسی‌کننده مجاز.",
    request=None, responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
))
class PaymentApproveAPIView(PaymentAppointmentsMixin, AppointmentActionAPIView):
    action = "payment_approve"


@extend_schema_view(post=extend_schema(
    description="رد رسید توسط بررسی‌کننده مجاز و آزاد شدن زمان. بارگذاری مجدد در صورت آزاد بودن زمان مجاز است.",
    request=PaymentRejectSerializer,
    responses={200: AppointmentReviewSerializer, **AUTH_ERRORS, **NOT_FOUND, **INVALID},
))
class PaymentRejectAPIView(PaymentAppointmentsMixin, AppointmentActionAPIView):
    action = "payment_reject"
    input_serializer = PaymentRejectSerializer
    note_field = "payment_note"


class ReceiptDownloadAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    @extend_schema(
        description="دانلود فایل خصوصی توسط مالک، مشاور رزرو یا بررسی‌کننده مجاز.",
        responses={(200, "application/octet-stream"): OpenApiTypes.BINARY, **AUTH_ERRORS, **NOT_FOUND},
    )
    def get(self, request, pk):
        appointment = get_object_or_404(appointment_details(), pk=pk)
        if request.user.pk not in (appointment.user_id, appointment.availability.consultant.user_id):
            if not can_review_payment(request.user):
                raise NotFound()
        if not appointment.payment_receipt:
            raise NotFound()
        try:
            stream = appointment.payment_receipt.open("rb")
        except FileNotFoundError as exc:
            raise NotFound() from exc

        response = FileResponse(stream, as_attachment=True, content_type="application/octet-stream")
        response["Cache-Control"] = "private, no-store"
        return response
