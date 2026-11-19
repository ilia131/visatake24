import re

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


PHONE_REGEX = re.compile(r"^\+[1-9]\d{7,14}$")


def normalize_phone_number(phone_number: str) -> str:
    """
    Normalize international phone number formatting.
    Expected final format: E.164, e.g. +989121234567
    """
    phone_number = phone_number.strip()

    for char in (" ", "-", "(", ")"):
        phone_number = phone_number.replace(char, "")

    if not PHONE_REGEX.fullmatch(phone_number):
        raise ValidationError(
            "Phone number must use international E.164 format."
        )

    return phone_number


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(
        self,
        phone_number,
        password=None,
        **extra_fields
    ):
        if not phone_number:
            raise ValueError("Phone number is required.")

        phone_number = normalize_phone_number(phone_number)

        user = self.model(
            phone_number=phone_number,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        phone_number,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        if not password:
            raise ValueError("Superuser password is required.")

        return self.create_user(
            phone_number=phone_number,
            password=password,
            **extra_fields
        )