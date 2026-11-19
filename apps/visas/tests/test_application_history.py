
import pytest

from apps.visas.models import VisaApplicationStatusHistory


@pytest.mark.django_db
def test_status_change_creates_history(
    admin_client,
    admin_user,
    application
):
    url = (
        f"/api/v1/visas/applications/"
        f"{application.tracking_code}/status/"
    )

    response = admin_client.patch(
        url,
        {
            "status": "under_review",
            "admin_notes": "مدارک در حال بررسی است."
        },
        format="json"
    )

    assert response.status_code == 200

    history = VisaApplicationStatusHistory.objects.get(
        application=application
    )

    assert history.previous_status == "submitted"
    assert history.new_status == "under_review"
    assert history.changed_by == admin_user
    assert history.note == "مدارک در حال بررسی است."


@pytest.mark.django_db
def test_same_status_does_not_create_duplicate_history(
    admin_client,
    application
):
    url = (
        f"/api/v1/visas/applications/"
        f"{application.tracking_code}/status/"
    )

    admin_client.patch(
        url,
        {"status": "under_review"},
        format="json"
    )

    admin_client.patch(
        url,
        {"status": "under_review"},
        format="json"
    )

    assert VisaApplicationStatusHistory.objects.filter(
        application=application
    ).count() == 1
