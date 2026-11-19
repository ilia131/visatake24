
from rest_framework import serializers
from django.utils import timezone
from apps.appointments.models import ConsultantAvailability

class AvailabilitySerializer(serializers.ModelSerializer):
    consultant_name = serializers.CharField(
        source="consultant.full_name",
        read_only=True,
    )

    consultant_slug = serializers.CharField(
        source="consultant.slug",
        read_only=True,
    )

    class Meta:
        model = ConsultantAvailability
        fields = [
            "id",
            "consultant",
            "consultant_name",
            "consultant_slug",
            "start_at",
            "end_at",
            "status",
        ]
        read_only_fields = fields


class AvailabilityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultantAvailability
        fields = [
            "id",
            "consultant",
            "start_at",
            "end_at",
        ]

    def validate(self, attrs):
        start_at = attrs.get("start_at", getattr(self.instance, "start_at", None))
        end_at = attrs.get("end_at", getattr(self.instance, "end_at", None))
        if end_at <= start_at:
            raise serializers.ValidationError("زمان پایان باید بعد از زمان شروع باشد.")
        if "start_at" in attrs and start_at <= timezone.now():
            raise serializers.ValidationError({"start_at": "زمان گذشته قابل ثبت نیست."})
        return attrs
