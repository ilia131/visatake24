
from django.contrib import admin

from apps.appointments.models import (
    ConsultantAvailability,
    Appointment,
)
from django.contrib import admin
from apps.consultants.models import ConsultantAssignment

@admin.register(ConsultantAvailability)
class ConsultantAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "consultant",
        "start_at",
        "end_at",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("consultant__full_name",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "availability",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "user__phone_number",
        "availability__consultant__full_name",
    )
    fields = (
        "user", "availability", "status", "consultation_fee", "user_note", "admin_note",
        "rejection_reason", "payment_note", "payment_reviewed_by", "payment_reviewed_at",
        "payment_submitted_at", "consultant_approved_at", "confirmed_at", "created_at", "updated_at",
    )
    readonly_fields = tuple(field for field in fields if field != "admin_note")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False






@admin.register(ConsultantAssignment)
class ConsultantAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "application",
        "consultant",
        "status",
        "is_active",
        "assigned_at",
    )
    list_filter = ("status", "is_active", "assigned_at")
    search_fields = (
        "consultant__full_name",
        "application__id",
    )
    readonly_fields = ("assigned_at", "updated_at")
