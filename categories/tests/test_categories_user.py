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
