from rest_framework import serializers
from apps.visas.models import VisaApplication ,VisaApplicationStatusHistory
from drf_spectacular.utils import extend_schema_field
class VisaApplicationCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaApplication

        fields = [
            "country",
            "visa_type",
            "travel_date",
            "return_date",
            "purpose",
            "additional_notes",
        ]

    def validate(self, attrs):
        travel_date = attrs.get("travel_date")
        return_date = attrs.get("return_date")

        if return_date and return_date < travel_date:
            raise serializers.ValidationError({
                "return_date": "تاریخ بازگشت نمی‌تواند قبل از تاریخ سفر باشد."
            })

        if not attrs["country"].is_active:
            raise serializers.ValidationError({
                "country": "این کشور در حال حاضر غیرفعال است."
            })

        return attrs


class VisaApplicationSerializer(serializers.ModelSerializer):

    country = serializers.SerializerMethodField()

    class Meta:
        model = VisaApplication

        fields = [
            "tracking_code",
            "country",
            "visa_type",
            "travel_date",
            "return_date",
            "purpose",
            "additional_notes",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = fields
    @extend_schema_field({
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "name_en": {"type": "string"},
                "slug": {"type": "string"},
                "flag": {"type": "string"},
            },
        })
    def get_country(self, obj):
        return {
            "id": obj.country.id,
            "name": obj.country.name,
            "name_en": obj.country.name_en,
            "slug": obj.country.slug,
            "flag": obj.country.flag,
        }
        
        
class VisaApplicationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=VisaApplication.Status.choices
    )

    admin_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=5000
    )
    def validate(self, attrs):
        if "status" not in attrs:
            raise serializers.ValidationError({
                "status": "وضعیت جدید الزامی است."
            })

        return attrs
    
    





class VisaApplicationStatusHistorySerializer(serializers.ModelSerializer):
    previous_status_display = serializers.CharField(
        source="get_previous_status_display",
        read_only=True
    )

    new_status_display = serializers.CharField(
        source="get_new_status_display",
        read_only=True
    )

    class Meta:
        model = VisaApplicationStatusHistory
        fields = [
            "id",
            "previous_status",
            "previous_status_display",
            "new_status",
            "new_status_display",
            "created_at",
        ]
        read_only_fields = fields
