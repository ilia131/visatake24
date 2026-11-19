import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


AUTH = "/api/v1/auth/"
PASSWORD = "Cedar-Harbor-7-quartz!"
CREDENTIALS = {"country_code": "IR", "phone_number": "09123456789", "password": PASSWORD}
REGISTRATION = {
    **CREDENTIALS,
    "first_name": "نیلوفر",
    "last_name": "کاوه",
    "password_confirmation": PASSWORD,
}
pytestmark = pytest.mark.django_db


def post(client, action, data=None):
    csrf = client.get(f"{AUTH}csrf/").data["csrfToken"]
    return client.post(f"{AUTH}{action}/", data, format="json", HTTP_X_CSRFTOKEN=csrf)


def test_registration_hashes_password_and_normalizes_unique_phone():
    client = APIClient(enforce_csrf_checks=True)
    response = post(client, "register", {**REGISTRATION, "role": "manager"})
    assert response.status_code == 201
    assert "password" not in response.data["user"]
    user = get_user_model().objects.get(phone_number="+989123456789")
    assert user.role == user.Role.CUSTOMER
    assert not user.is_phone_verified
    assert user.password != PASSWORD and user.check_password(PASSWORD)
    assert post(client, "register", {**REGISTRATION, "phone_number": "9123456789"}).status_code == 400
    assert get_user_model().objects.count() == 1


@pytest.mark.parametrize(("changes", "field"), [
    ({"password": "12345678", "password_confirmation": "12345678"}, "password"),
    ({"password_confirmation": "different"}, "password_confirmation"),
    ({"phone_number": "123"}, "phone_number"),
    ({"country_code": "US"}, "phone_number"),
])
def test_registration_validation(changes, field):
    response = post(APIClient(), "register", {**REGISTRATION, **changes})
    assert response.status_code == 400
    assert field in response.data
    assert get_user_model().objects.count() == 0


def test_login_validation_and_generic_failure():
    user = get_user_model().objects.create_user("+989123456789", PASSWORD)
    client = APIClient()
    wrong = post(client, "login", {**CREDENTIALS, "password": "wrong"})
    unknown = post(client, "login", {**CREDENTIALS, "phone_number": "09123456780"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.data == unknown.data
    assert post(client, "login", {**CREDENTIALS, "phone_number": "123"}).status_code == 400
    assert post(client, "login", {**CREDENTIALS, "country_code": "US"}).status_code == 400
    user.is_active = False
    user.save(update_fields=["is_active"])
    disabled = post(client, "login", CREDENTIALS)
    assert disabled.status_code == 401
    assert disabled.data == unknown.data


def test_protected_cookie_session_rotation_and_logout(settings):
    settings.JWT_COOKIE_SECURE = True
    user = get_user_model().objects.create_user("+989123456789", PASSWORD, role="manager")
    client = APIClient(enforce_csrf_checks=True)
    assert client.post(f"{AUTH}login/", CREDENTIALS, format="json").status_code == 403
    login = post(client, "login", CREDENTIALS)
    assert login.status_code == 200
    assert login.data["user"]["role"] == user.role
    for cookie in (settings.JWT_ACCESS_COOKIE, settings.JWT_REFRESH_COOKIE):
        assert login.cookies[cookie]["httponly"]
        assert login.cookies[cookie]["secure"]
    old_token = client.cookies[settings.JWT_REFRESH_COOKIE].value
    assert client.get(f"{AUTH}me/").data["user"]["id"] == user.pk
    assert client.get("/api/v1/appointments/admin/payments/").status_code == 200
    assert client.post(f"{AUTH}token/refresh/").status_code == 403
    assert post(client, "token/refresh").status_code == 200
    rotated = client.cookies[settings.JWT_REFRESH_COOKIE].value
    assert rotated != old_token
    assert client.post(f"{AUTH}logout/").status_code == 403

    replay = APIClient()
    replay.cookies[settings.JWT_REFRESH_COOKIE] = old_token
    assert post(replay, "token/refresh").status_code == 401

    del client.cookies[settings.JWT_ACCESS_COOKIE]
    assert post(client, "logout").status_code == 200
    assert not client.cookies[settings.JWT_REFRESH_COOKIE].value
    replay.cookies[settings.JWT_REFRESH_COOKIE] = rotated
    assert post(replay, "token/refresh").status_code == 401
    assert client.get(f"{AUTH}me/").status_code == 401


def test_login_limit_applies_to_normalized_phone_even_across_source_ips():
    client = APIClient()
    csrf = client.get(f"{AUTH}csrf/").data["csrfToken"]
    for index in range(9):
        response = client.post(
            f"{AUTH}login/",
            {**CREDENTIALS, "phone_number": "9123456789" if index % 2 else "09123456789"},
            format="json", HTTP_X_CSRFTOKEN=csrf, REMOTE_ADDR=f"10.0.0.{index + 1}",
        )
        assert response.status_code == (401 if index < 8 else 429)
    assert int(response.headers["Retry-After"]) > 0


def test_otp_paths_retired_and_legacy_user_preserved():
    user = get_user_model().objects.create_user("+989123456789", is_phone_verified=True)
    client = APIClient()
    assert client.post(f"{AUTH}otp/request/").status_code == 404
    assert client.post(f"{AUTH}otp/verify/").status_code == 404
    assert post(client, "login", CREDENTIALS).status_code == 401
    assert post(client, "register", REGISTRATION).status_code == 400
    user.refresh_from_db()
    assert user.is_phone_verified and not user.has_usable_password()


def test_ip_limiter_ignores_untrusted_forwarded_prefix(settings):
    from unittest.mock import patch

    from django.test import RequestFactory

    from apps.accounts.services.authentication import client_ip

    request = RequestFactory().get(
        "/", REMOTE_ADDR="172.16.0.3", HTTP_X_FORWARDED_FOR="203.0.113.5, 192.0.2.10, 172.16.0.2",
    )
    assert client_ip(request) == "172.16.0.3"
    with patch.object(settings, "AUTH_PROXY_HOPS", 2):
        assert client_ip(request) == "192.0.2.10"
