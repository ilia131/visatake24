from rest_framework import serializers

from apps.visas.models import VisaApplicationDocument


class DashboardDocumentSerializer(serializers.ModelSerializer):
    tracking_code = serializers.CharField(
        source="application.tracking_code",
        read_only=True,
    )
    document_type_display = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )

    class Meta:
        model = VisaApplicationDocument
        fields = [
            "id",
            "tracking_code",
            "document_type",
            "document_type_display",
            "status",
            "status_display",
            "admin_notes",
            "uploaded_at",
            "updated_at",
        ]