
import pytest


@pytest.mark.django_db
def test_list_active_countries(api_client, country):
    response = api_client.get("/api/v1/visas/countries/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == "آلمان"


@pytest.mark.django_db
def test_inactive_country_is_not_visible(api_client, country):
    country.is_active = False
    country.save()

    response = api_client.get("/api/v1/visas/countries/")

    assert response.status_code == 200
    assert len(response.data) == 0
