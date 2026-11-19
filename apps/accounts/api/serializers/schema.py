
from rest_framework import serializers


class SuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class CSRFResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    csrfToken = serializers.CharField()


class UserResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    phone_number = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()
    is_phone_verified = serializers.BooleanField()


class MeResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    user = UserResponseSerializer()
