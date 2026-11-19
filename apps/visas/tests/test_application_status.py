
import pytest
from rest_framework.test import APIClient

from apps.visas.models import VisaApplication


@pytest.fixture
def admin_user(db):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    return User.objects.create_superuser(
        phone_number="+989121234569",
        password="test123456"
    )


@pytest.fixture
def admin_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def application(user, country):
    return VisaApplication.objects.create(
        user=user,
        country=country,
        visa_type="Tourist",
        travel_date="2027-05-10",
        return_date="2027-05-20",
        purpose="Tourism",
        additional_notes=""
    )


@pytest.mark.django_db
def test_admin_can_update_application_status(
    admin_client,
    application
):
    url = (
        f"/api/v1/visas/applications/"
        f"{application.tracking_code}/status/"
    )

    response = admin_client.patch(url, {
        "status": "under_review",
        "admin_notes": "مدارک در حال بررسی است."
    }, format="json")

    assert response.status_code == 200

    application.refresh_from_db()

    assert application.status == "under_review"
    assert application.admin_notes == "مدارک در حال بررسی است."


@pytest.mark.django_db
def test_normal_user_cannot_update_status(
    authenticated_client,
    application
):
    url = (
        f"/api/v1/visas/applications/"
        f"{application.tracking_code}/status/"
    )

    response = authenticated_client.patch(url, {
        "status": "approved"
    }, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_cannot_update_nonexistent_application(
    admin_client
):
    url = "/api/v1/visas/applications/VY-INVALID/status/"

    response = admin_client.patch(url, {
        "status": "approved"
    }, format="json")

    assert response.status_code == 404


@pytest.mark.django_db
def test_admin_cannot_send_invalid_status(
    admin_client,
    application
):
    url = (
        f"/api/v1/visas/applications/"
        f"{application.tracking_code}/status/"
    )

    response = admin_client.patch(url, {
        "status": "invalid_status"
    }, format="json")

    assert response.status_code == 400
