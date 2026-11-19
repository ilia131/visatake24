from django.conf import settings
from django.urls import reverse
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.appointments.models import Appointment
from apps.appointments.receipts import validate_receipt


class AppointmentCreateSerializer(serializers.Serializer):
    availability_id = serializers.IntegerField(min_value=1)
    user_note = serializers.CharField(required=False, allow_blank=True)


class AppointmentSerializer(serializers.ModelSerializer):
    payment_card = serializers.SerializerMethodField()
    payment_receipt_url = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_payment_card(self, obj):
        request = self.context.get("request")
        if request and request.user.pk == obj.user_id and obj.consultant_approved_at:
            return settings.APPOINTMENT_PAYMENT_CARD
        return None

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_payment_receipt_url(self, obj):
        if not obj.payment_receipt:
            return None
        path = reverse("appointment-receipt-download", kwargs={"pk": obj.pk})
        request = self.context.get("request")
        return request.build_absolute_uri(path) if request else path

    class Meta:
        model = Appointment
        fields = [
            "id", "availability", "status", "user_note", "consultation_fee",
            "rejection_reason", "payment_card", "payment_receipt_url", "payment_note",
            "payment_submitted_at", "payment_reviewed_at", "consultant_approved_at",
            "confirmed_at", "created_at", "updated_at",
        ]
        read_only_fields = fields


class AppointmentReviewSerializer(AppointmentSerializer):
    applicant_name = serializers.SerializerMethodField()
    consultant_name = serializers.CharField(source="availability.consultant.full_name", read_only=True)
    start_at = serializers.DateTimeField(source="availability.start_at", read_only=True)
    end_at = serializers.DateTimeField(source="availability.end_at", read_only=True)

    @extend_schema_field(str)
    def get_applicant_name(self, obj):
        return obj.user.get_full_name()

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + [
            "applicant_name", "consultant_name", "start_at", "end_at", "payment_reviewed_by",
        ]
        read_only_fields = fields


class ReceiptUploadSerializer(serializers.Serializer):
    payment_receipt = serializers.FileField(validators=[validate_receipt])


class ConsultantRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(max_length=4000)


class PaymentRejectSerializer(serializers.Serializer):
    payment_note = serializers.CharField(max_length=4000)


class AppointmentFilterSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appointment.Status.choices, required=False)
    date = serializers.DateField(required=False, help_text="تاریخ جلسه به وقت تهران")
