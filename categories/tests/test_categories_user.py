import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_user_can_list_active_categories(
    api_client, category_active, category_inactive
):
    url = reverse("category-list")
    response = api_client.get(url)
    assert response.status_code == 200

    ids = [c["id"] for c in response.json()["results"]]
    assert category_active.id in ids
    assert category_inactive.id not in ids


@pytest.mark.django_db
def test_user_can_get_active_category_detail(api_client, category_active):
    url = reverse("category-detail", args=[category_active.id])
    response = api_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_active.id
    assert data["name"] == "Active Category"


@pytest.mark.django_db
def test_user_cannot_get_inactive_category_detail(api_client, category_inactive):
    url = reverse("category-detail", args=[category_inactive.id])
    response = api_client.get(url)
    assert response.status_code == 404
