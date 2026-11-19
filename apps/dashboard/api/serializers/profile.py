from rest_framework import serializers


class DashboardProfileSerializer(serializers.Serializer):
    phone_number = serializers.CharField(read_only=True)
    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )
    first_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save(
            update_fields=list(validated_data.keys())
        )

        return instance