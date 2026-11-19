
from rest_framework import serializers

from apps.consultants.models import Consultant


class ConsultantAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = [
            "id",
            "user",
            "full_name",
            "slug",
            "title",
            "bio",
            "avatar",
            "specialties",
            "experience_years",
            "consultation_fee",
            "is_active",
            "is_verified",
            "display_order",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_experience_years(self, value):
        if value > 70:
            raise serializers.ValidationError(
                "سابقه کاری نمی‌تواند بیشتر از ۷۰ سال باشد."
            )
        return value
