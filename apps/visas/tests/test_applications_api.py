
import pytest


@pytest.mark.django_db
def test_create_visa_application(
    authenticated_client,
    country,
    user,
):
    payload = {
        "country": country.id,
        "visa_type": "Tourist",
        "travel_date": "2027-02-15",
        "return_date": "2027-02-25",
        "purpose": "Tourism",
        "additional_notes": "First trip",
    }

    response = authenticated_client.post(
        "/api/v1/visas/applications/",
        payload,
        format="json",
    )

    assert response.status_code == 201
    assert response.data["tracking_code"].startswith("VY-")
    assert response.data["country"]["name"] == "آلمان"

    assert user.visa_applications.count() == 1


@pytest.mark.django_db
def test_user_can_list_own_applications(
    authenticated_client,
    country,
    user,
):
    from apps.visas.models import VisaApplication

    application = VisaApplication.objects.create(
        user=user,
        country=country,
        visa_type="Tourist",
        travel_date="2027-02-15",
        purpose="Tourism",
    )

    response = authenticated_client.get(
        "/api/v1/visas/applications/"
    )

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["tracking_code"] == application.tracking_code


@pytest.mark.django_db
def test_user_cannot_see_another_users_application(
    authenticated_client,
    another_user,
    country,
):
    from apps.visas.models import VisaApplication

    application = VisaApplication.objects.create(
        user=another_user,
        country=country,
        visa_type="Tourist",
        travel_date="2027-02-15",
        purpose="Tourism",
    )

    response = authenticated_client.get(
        f"/api/v1/visas/applications/{application.tracking_code}/"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_application(
    api_client,
    country,
):
    payload = {
        "country": country.id,
        "visa_type": "Tourist",
        "travel_date": "2027-02-15",
        "purpose": "Tourism",
    }

    response = api_client.post(
        "/api/v1/visas/applications/",
        payload,
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_return_date_cannot_be_before_travel_date(
    authenticated_client,
    country,
):
    payload = {
        "country": country.id,
        "visa_type": "Tourist",
        "travel_date": "2027-02-25",
        "return_date": "2027-02-15",
        "purpose": "Tourism",
    }

    response = authenticated_client.post(
        "/api/v1/visas/applications/",
        payload,
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_can_list_own_applications(
    authenticated_client,
    country,
    user,
):
    from apps.visas.models import VisaApplication

    application = VisaApplication.objects.create(
        user=user,
        country=country,
        visa_type="Tourist",
        travel_date="2027-02-15",
        purpose="Tourism",
    )

    response = authenticated_client.get(
        "/api/v1/visas/applications/"
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1

    assert (
        response.data["results"][0]["tracking_code"]
        == application.tracking_code
    )
    
@pytest.mark.django_db
def test_applications_pagination(
    authenticated_client,
    country,
    user,
):
    from apps.visas.models import VisaApplication

    for index in range(12):
        VisaApplication.objects.create(
            user=user,
            country=country,
            visa_type="Tourist",
            travel_date="2027-02-15",
            purpose=f"Tourism {index}",
        )

    response = authenticated_client.get(
        "/api/v1/visas/applications/"
    )

    assert response.status_code == 200
    assert response.data["count"] == 12
    assert len(response.data["results"]) == 10

    second_page = authenticated_client.get(
        "/api/v1/visas/applications/?page=2"
    )

    assert second_page.status_code == 200
    assert len(second_page.data["results"]) == 2