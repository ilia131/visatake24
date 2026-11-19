
from rest_framework import serializers

from apps.consultants.models import (
    Consultant,
    ConsultantSpecialty,
)


class ConsultantSpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultantSpecialty
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]


class ConsultantSerializer(serializers.ModelSerializer):
    specialties = ConsultantSpecialtySerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Consultant
        fields = [
            "id",
            "full_name",
            "slug",
            "title",
            "bio",
            "avatar",
            "specialties",
            "experience_years",
            "consultation_fee",
            "is_verified",
        ]
        read_only_fields = fields
