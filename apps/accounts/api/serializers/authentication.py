import re

import phonenumbers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import override
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    country_code = serializers.CharField(min_length=2, max_length=2)
    phone_number = serializers.CharField(max_length=32)
    password = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate(self, attrs):
        region = attrs["country_code"].upper()
        number = attrs["phone_number"]
        message = "شماره تلفن برای کشور انتخاب‌شده معتبر نیست."
        if region not in phonenumbers.SUPPORTED_REGIONS or not re.fullmatch(r"[0-9 ()-]+", number):
            raise serializers.ValidationError({"phone_number": message})
        try:
            parsed = phonenumbers.parse(number, region)
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError({"phone_number": message}) from None
        if not phonenumbers.is_valid_number_for_region(parsed, region):
            raise serializers.ValidationError({"phone_number": message})
        attrs["phone_number"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        del attrs["country_code"]
        return attrs


class RegisterSerializer(LoginSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password_confirmation = serializers.CharField(write_only=True, trim_whitespace=False, max_length=128)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.pop("password_confirmation") != attrs["password"]:
            raise serializers.ValidationError({"password_confirmation": "رمز عبور و تکرار آن یکسان نیستند."})
        user = get_user_model()(
            phone_number=attrs["phone_number"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        try:
            with override("fa"):
                validate_password(attrs["password"], user=user)
        except ValidationError as exc:
            raise serializers.ValidationError({"password": exc.messages}) from None
        return attrs
