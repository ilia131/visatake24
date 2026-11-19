import pytest
from rest_framework.test import APIClient

from apps.consultants.models import Consultant


@pytest.mark.django_db
def test_admin_can_manage_nonnegative_fee(django_user_model):
    owner = django_user_model.objects.create_user(phone_number="+989100000001")
    admin = django_user_model.objects.create_user(phone_number="+989100000002", is_staff=True)
    consultant = Consultant.objects.create(full_name="Consultant", slug="consultant", is_verified=True)
    url = f"/api/v1/consultants/manage/{consultant.pk}/"
    client = APIClient()
    client.force_authenticate(owner)
    assert client.patch(url, {"consultation_fee": 1000}).status_code == 403
    client.force_authenticate(admin)
    assert client.get("/api/v1/consultants/manage/").status_code == 200
    assert client.patch(url, {"consultation_fee": -1}).status_code == 400
    response = client.patch(url, {"consultation_fee": 120000})
    assert response.status_code == 200
    assert response.data["consultation_fee"] == "120000"
    assert client.get("/api/v1/consultants/consultant/").data["consultation_fee"] == "120000"
