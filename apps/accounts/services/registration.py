from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError


def register_user(**credentials):
    user_model = get_user_model()
    try:
        with transaction.atomic():
            return user_model.objects.create_user(**credentials)
    except IntegrityError:
        if not user_model.objects.filter(phone_number=credentials["phone_number"]).exists():
            raise
        raise ValidationError({"phone_number": "این شماره تلفن قبلاً ثبت شده است."}) from None
