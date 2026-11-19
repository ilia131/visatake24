
import pytest

from unittest.mock import patch
from apps.accounts.models import OTPCode
from apps.accounts.services.otp import request_otp
from apps.accounts.services.authentication import (
    verify_otp,
    OTPError,
)


@pytest.mark.django_db
def test_successful_otp_login():

    with patch(
        "apps.accounts.services.otp.send_otp"
    ) as sender:

        request_otp(
            phone_number="+989121234567"
        )

        code = sender.call_args.kwargs["code"]

    user, created = verify_otp(
        phone_number="+989121234567",
        code=code,
    )

    assert created is True
    assert user.phone_number == "+989121234567"
    assert user.is_phone_verified is True


@pytest.mark.django_db
def test_existing_user_login():

    from django.contrib.auth import get_user_model

    User = get_user_model()

    existing_user = User.objects.create_user(
        phone_number="+989121234567"
    )

    with patch(
        "apps.accounts.services.otp.send_otp"
    ) as sender:

        request_otp(
            phone_number=existing_user.phone_number
        )

        code = sender.call_args.kwargs["code"]

    user, created = verify_otp(
        phone_number=existing_user.phone_number,
        code=code,
    )

    assert created is False
    assert user.id == existing_user.id


@pytest.mark.django_db
def test_wrong_otp():

    with patch(
        "apps.accounts.services.otp.send_otp"
    ):

        request_otp(
            phone_number="+989121234567"
        )

    with pytest.raises(OTPError):

        verify_otp(
            phone_number="+989121234567",
            code="000000",
        )


@pytest.mark.django_db
def test_used_otp_cannot_be_reused():

    with patch(
        "apps.accounts.services.otp.send_otp"
    ) as sender:

        request_otp(
            phone_number="+989121234567"
        )

        code = sender.call_args.kwargs["code"]

    verify_otp(
        phone_number="+989121234567",
        code=code,
    )

    with pytest.raises(OTPError):

        verify_otp(
            phone_number="+989121234567",
            code=code,
        )
