import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_admin_can_list_all_categories(
    admin_api_client, category_active, category_inactive
):
    url = reverse("admin-category-list-create")
    response = admin_api_client.get(url)
    assert response.status_code == 200
    ids = [c["id"] for c in response.json()["results"]]
    assert category_active.id in ids
    assert category_inactive.id in ids
