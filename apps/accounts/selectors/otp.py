from apps.accounts.models import OTPCode


def get_latest_valid_otp(*, phone_number):

    return OTPCode.objects.filter(
        phone_number=phone_number,
        is_used=False,
    ).order_by("-created_at").first()