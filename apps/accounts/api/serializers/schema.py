
from rest_framework import serializers


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class CSRFResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    csrfToken = serializers.CharField()


class OTPRequestResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class OTPVerifyResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    is_new_user = serializers.BooleanField()


class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    phone_number = serializers.CharField()
    email = serializers.EmailField(allow_null=True)
    role = serializers.CharField()
    is_phone_verified = serializers.BooleanField()


class MeResponseSerializer(serializers.Serializer):
    user = UserResponseSerializer()


class LogoutResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
