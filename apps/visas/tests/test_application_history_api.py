
import pytest
from apps.visas.models import VisaApplicationStatusHistory


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