from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.accounts.managers import normalize_phone_number
from apps.accounts.models import OTPCode
from apps.accounts.services.otp import OTPError

User = get_user_model()

MAX_OTP_ATTEMPTS = 5


def verify_otp(*, phone_number: str, code: str):
    phone_number = normalize_phone_number(phone_number)

    error_message = None
    result = None

    with transaction.atomic():
        otp = (
            OTPCode.objects
            .filter(
                phone_number=phone_number,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            error_message = "کد تأیید معتبر نیست."

        elif otp.is_expired:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            error_message = "کد تأیید منقضی شده است."

        elif otp.attempts >= MAX_OTP_ATTEMPTS:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            error_message = "تعداد تلاش‌های شما بیش از حد مجاز است."

        elif not check_password(code, otp.code_hash):
            otp.attempts += 1

            if otp.attempts >= MAX_OTP_ATTEMPTS:
                otp.is_used = True

            otp.save(update_fields=["attempts", "is_used"])

            error_message = "کد تأیید اشتباه است."

        else:
            otp.is_used = True
            otp.save(update_fields=["is_used"])

            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    "is_active": True,
                    "is_phone_verified": True,
                },
            )

            if not user.is_active:
                error_message = "حساب کاربری غیرفعال است."
            else:
                if not user.is_phone_verified:
                    user.is_phone_verified = True
                    user.save(update_fields=["is_phone_verified"])

                result = (user, created)

    # خطا خارج از تراکنش پرتاب می‌شود تا تغییرات بالا Rollback نشوند.
    if error_message:
        raise OTPError(error_message)

    return result