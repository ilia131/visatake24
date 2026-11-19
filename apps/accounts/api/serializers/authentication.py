
import re

from rest_framework import serializers


class OTPRequestSerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=16
    )

    def validate_phone_number(self, value):

        from apps.accounts.managers import normalize_phone_number

        try:
            return normalize_phone_number(value)
        except Exception:
            raise serializers.ValidationError(
                "Invalid international phone number."
            )


class OTPVerifySerializer(serializers.Serializer):

    phone_number = serializers.CharField(
        max_length=16
    )

    code = serializers.RegexField(
        regex=r"^\d{6}$",
        error_messages={
            "invalid": "OTP must contain exactly 6 digits."
        },
    )

    def validate_phone_number(self, value):

        from apps.accounts.managers import normalize_phone_number

        try:
            return normalize_phone_number(value)
        except Exception:
            raise serializers.ValidationError(
                "Invalid international phone number."
            )
