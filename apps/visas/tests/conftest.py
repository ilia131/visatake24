
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.visas.models import Country
from apps.visas.models import VisaApplication

User = get_user_model()
@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        phone_number="+989121234569",
        password="test123456"
    )


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        phone_number="+989121234567",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        phone_number="+989121234568",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def country(db):
    return Country.objects.create(
        name="آلمان",
        name_en="Germany",
        slug="germany",
        flag="🇩🇪",
        description="کشور آلمان",
        is_active=True,
    )

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