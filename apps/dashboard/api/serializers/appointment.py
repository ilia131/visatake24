from rest_framework import serializers

from apps.appointments.models import Appointment


class DashboardAppointmentSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(
        source="availability.consultant.full_name",
        read_only=True,
    )
    consultant_title = serializers.CharField(
        source="availability.consultant.title",
        read_only=True,
    )
    start_at = serializers.DateTimeField(
        source="availability.start_at",
        read_only=True,
    )
    end_at = serializers.DateTimeField(
        source="availability.end_at",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "consultant_name",
            "consultant_title",
            "start_at",
            "end_at",
            "status",
            "status_display",
            "user_note",
            "created_at",
        ]