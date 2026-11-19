from datetime import timedelta
from io import BytesIO

import pytest
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from apps.visas.models import VisaApplicationDocument, VisaApplicationStatusHistory


@pytest.mark.django_db
def test_user_can_see_own_application_history(
    admin_client,
    admin_user,
    authenticated_client,
    application,
):
    VisaApplicationStatusHistory.objects.create(
        application=application,
        previous_status="submitted",
        new_status="under_review",
        changed_by=admin_user,
        note="یادداشت محرمانه مدیر",
    )

    url = (
        f"/api/v1/visas/applications/"
        f"{application.tracking_code}/history/"
    )

    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["new_status"] == "under_review"
    assert "note" not in response.data[0]
    assert "changed_by" not in response.data[0]


@pytest.mark.django_db
def test_user_cannot_see_another_users_history(
    authenticated_client,
    another_user,
    country,
    admin_user,
):
    from apps.visas.models import VisaApplication

    other_application = VisaApplication.objects.create(
        user=another_user,
        country=country,
        visa_type="Tourist",
        travel_date="2027-05-10",
        purpose="Tourism",
    )

    VisaApplicationStatusHistory.objects.create(
        application=other_application,
        previous_status="submitted",
        new_status="under_review",
        changed_by=admin_user,
    )

    url = (
        f"/api/v1/visas/applications/"
        f"{other_application.tracking_code}/history/"
    )

    response = authenticated_client.get(url)

    assert response.status_code == 403
    assert response.data["detail"] == "شما اجازه مشاهده تاریخچه این پرونده را ندارید."

@pytest.mark.django_db
def test_visa_application_from_submission_to_dashboard_history(
    authenticated_client, admin_user, another_user, country, tmp_path, monkeypatch,
):
    document_field = VisaApplicationDocument._meta.get_field("file")
    monkeypatch.setattr(document_field, "storage", FileSystemStorage(location=tmp_path))
    manager = APIClient()
    manager.force_authenticate(admin_user)
    outsider = APIClient()
    outsider.force_authenticate(another_user)
    applications = "/api/v1/visas/applications/"
    response = authenticated_client.post(applications, {
        "country": country.pk,
        "visa_type": "Tourist",
        "travel_date": (timezone.localdate() + timedelta(days=60)).isoformat(),
        "purpose": "Tourism",
    }, format="json")
    assert response.status_code == 201
    tracking_code = response.data["tracking_code"]
    detail = f"{applications}{tracking_code}/"

    photo = BytesIO()
    Image.new("RGB", (3, 3)).save(photo, format="PNG")
    response = authenticated_client.post(f"{detail}documents/", {
        "document_type": "photo",
        "file": SimpleUploadedFile("photo.png", photo.getvalue(), content_type="image/png"),
    }, format="multipart")
    assert response.status_code == 201
    assert outsider.get(f"{detail}documents/").status_code == 404
    response = manager.patch(f"{detail}status/", {"status": "under_review"}, format="json")
    assert response.status_code == 200

    dashboard = f"/api/v1/dashboard/applications/{tracking_code}/"
    response = authenticated_client.get(dashboard)
    assert response.status_code == 200
    assert response.data["status"] == "under_review"
    response = authenticated_client.get(f"{detail}history/")
    assert response.status_code == 200
    assert response.data[0]["new_status"] == "under_review"
