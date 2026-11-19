from http import HTTPStatus
from unittest.mock import Mock

import pytest
from django.contrib.auth.hashers import check_password
from django.urls import reverse

from apps.accounts.models import OTPCode


@pytest.mark.django_db
@pytest.mark.parametrize("provider_status", [1, 0])
def test_otp_request_uses_smsir(client, settings, monkeypatch, provider_status):
    settings.SMSIR_API_KEY = "test-key"
    settings.SMSIR_OTP_TEMPLATE_ID = "123"
    response = Mock(status_code=200)
    response.json.return_value = {
        "status": provider_status,
        "data": {"messageId": 12345},
    }
    post = Mock(return_value=response)
    monkeypatch.setattr("apps.accounts.services.sms.requests.post", post)
    phone = "+989120000000"

    result = client.post(reverse("otp-request"), {"phone_number": phone})

    assert post.call_args.args == ("https://api.sms.ir/v1/send/verify",)
    payload = post.call_args.kwargs["json"]
    assert payload["mobile"] == "09120000000"
    assert payload["templateId"] == 123
    parameter, = payload["parameters"]
    assert parameter["name"] == "CODE"
    assert len(parameter["value"]) == 6
    assert parameter["value"] not in result.content.decode()

    if provider_status == 1:
        assert result.status_code == HTTPStatus.OK
        otp = OTPCode.objects.get(phone_number=phone)
        assert check_password(parameter["value"], otp.code_hash)
    else:
        assert result.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert not OTPCode.objects.filter(phone_number=phone).exists()
