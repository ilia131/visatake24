from unittest.mock import patch

import pytest

from apps.accounts.services.otp import (
    request_otp,
    OTPError,
)


@pytest.mark.django_db
@patch("apps.accounts.services.otp.send_otp")
def test_otp_resend_cooldown(mock_send_otp):

    phone = "+989121234567"

    # درخواست اول
    request_otp(phone_number=phone)

    # درخواست دوم بلافاصله بعد از اول
    with pytest.raises(OTPError):
        request_otp(phone_number=phone)

    # ارسال پیامک فقط باید یک بار اتفاق افتاده باشد
    assert mock_send_otp.call_count == 1