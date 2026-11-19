
import secrets
import logging

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import OTPCode
from apps.accounts.managers import normalize_phone_number


logger = logging.getLogger(__name__)


OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 2
OTP_RESEND_SECONDS = 60
OTP_MAX_ATTEMPTS = 5
OTP_MAX_PER_HOUR = 5


class OTPError(Exception):
    pass


def generate_otp():
    return f"{secrets.randbelow(10 ** OTP_LENGTH):06d}"


def send_otp(*, phone_number, code):
    """
    Development delivery adapter.
    Replace with an SMS provider in production.
    Never expose OTP in API responses.
    """
    if not settings.DEBUG:
        raise RuntimeError(
            "Development OTP delivery is disabled in production."
        )

    logger.warning(
        "VOYAVISA DEVELOPMENT OTP | %s | %s",
        phone_number,
        code,
    )


@transaction.atomic
def request_otp(*, phone_number):

    try:
        phone_number = normalize_phone_number(phone_number)
    except ValidationError as exc:
        raise OTPError("Invalid phone number.") from exc

    now = timezone.now()

    recent_otp = OTPCode.objects.filter(
        phone_number=phone_number,
        created_at__gte=now - timedelta(seconds=OTP_RESEND_SECONDS),
    ).exists()

    if recent_otp:
        raise OTPError(
            "Please wait before requesting another code."
        )

    hourly_count = OTPCode.objects.filter(
        phone_number=phone_number,
        created_at__gte=now - timedelta(hours=1),
    ).count()

    if hourly_count >= OTP_MAX_PER_HOUR:
        raise OTPError(
            "OTP request limit exceeded."
        )

    code = generate_otp()

    OTPCode.objects.filter(
        phone_number=phone_number,
        is_used=False,
    ).update(is_used=True)

    otp = OTPCode.objects.create(
        phone_number=phone_number,
        code_hash=make_password(code),
        expires_at=now + timedelta(
            minutes=OTP_EXPIRY_MINUTES
        ),
    )

    send_otp(
        phone_number=phone_number,
        code=code,
    )

    return otp
