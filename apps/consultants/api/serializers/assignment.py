
from rest_framework import serializers
from apps.consultants.models import ConsultantAssignment


class AssignmentSerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(
        source="consultant.full_name",
        read_only=True,
    )

    class Meta:
        model = ConsultantAssignment
        fields = [
            "id",
            "application",
            "consultant",
            "consultant_name",
            "status",
            "is_active",
            "admin_note",
            "consultant_note",
            "assigned_at",
            "updated_at",
        ]
        read_only_fields = fields


class AssignmentCreateSerializer(serializers.Serializer):
    application_id = serializers.IntegerField(min_value=1)
    consultant_id = serializers.IntegerField(min_value=1)


class AssignmentStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=ConsultantAssignment.Status.choices
    )
    consultant_note = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000,
    )
