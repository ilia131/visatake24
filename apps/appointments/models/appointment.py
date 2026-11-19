
from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.appointments.receipts import receipt_path, receipt_storage

OCCUPYING_STATUSES = ("pending", "awaiting_payment", "payment_submitted", "confirmed")

from apps.appointments.models.availability import (
    ConsultantAvailability,
)


class Appointment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار تأیید مشاور"
        AWAITING_PAYMENT = "awaiting_payment", "در انتظار پرداخت"
        PAYMENT_SUBMITTED = "payment_submitted", "در انتظار بررسی رسید"
        PAYMENT_REJECTED = "payment_rejected", "پرداخت رد شده"
        REJECTED = "rejected", "درخواست رد شده"
        CONFIRMED = "confirmed", "رزرو قطعی"
        CANCELLED = "cancelled", "لغو شده"
        COMPLETED = "completed", "انجام شده"

    availability = models.ForeignKey(
        ConsultantAvailability,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="appointments",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    user_note = models.TextField(blank=True)

    admin_note = models.TextField(blank=True)

    consultation_fee = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    rejection_reason = models.TextField(blank=True)
    payment_receipt = models.FileField(storage=receipt_storage, upload_to=receipt_path, blank=True)
    payment_note = models.TextField(blank=True)
    payment_submitted_at = models.DateTimeField(null=True, blank=True)
    payment_reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_appointment_payments",
    )
    payment_reviewed_at = models.DateTimeField(null=True, blank=True)
    consultant_approved_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["availability"],
                condition=Q(status__in=OCCUPYING_STATUSES),
                name="unique_active_appointment_per_slot",
            ),
        ]

        permissions = [("review_payment", "Can review appointment payments")]

        indexes = [
            models.Index(
                fields=["user", "status"],
                name="appointment_user_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.availability}"


class AppointmentHistory(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="history")
    previous_status = models.CharField(max_length=20, choices=Appointment.Status.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=Appointment.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]
