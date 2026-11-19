from rest_framework import serializers

from apps.visas.models import (
    VisaApplication,
    VisaApplicationStatusHistory,
)
from apps.consultants.models import ConsultantAssignment


class ApplicationListSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = VisaApplication
        fields = [
            "tracking_code",
            "country_name",
            "visa_type",
            "travel_date",
            "return_date",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source="country.name",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    consultant = serializers.SerializerMethodField()

    class Meta:
        model = VisaApplication
        fields = [
            "tracking_code",
            "country_name",
            "visa_type",
            "travel_date",
            "return_date",
            "purpose",
            "additional_notes",
            "status",
            "status_display",
            "created_at",
            "updated_at",
            "consultant",
        ]

    def get_consultant(self, obj):
        assignment = (
            ConsultantAssignment.objects
            .filter(application=obj, is_active=True)
            .select_related("consultant")
            .first()
        )

        if not assignment:
            return None

        return {
            "full_name": assignment.consultant.full_name,
            "title": assignment.consultant.title,
            "slug": assignment.consultant.slug,
            "status": assignment.status,
            "consultant_note": assignment.consultant_note,
        }


class ApplicationHistorySerializer(
    serializers.ModelSerializer
):
    previous_status_display = serializers.CharField(
        source="get_previous_status_display",
        read_only=True,
    )
    new_status_display = serializers.CharField(
        source="get_new_status_display",
        read_only=True,
    )

    class Meta:
        model = VisaApplicationStatusHistory
        fields = [
            "previous_status",
            "previous_status_display",
            "new_status",
            "new_status_display",
            "note",
            "created_at",
        ]