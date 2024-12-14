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


@pytest.mark.django_db
def test_admin_can_create_category(admin_api_client, category_active):
    url = reverse("admin-category-list-create")
    payload = {
        "name": "New Category",
        "slug": "new-category",
        "is_active": True,
        "parent": category_active.id,
    }
    response = admin_api_client.post(url, payload, format="json")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"
    assert data["slug"] == "new-category"
    assert data["is_active"] == True


@pytest.mark.django_db
def test_admin_can_retrieve_update_delete_category(admin_api_client, category_active):
    detail_url = reverse("admin-category-detail", args=[category_active.id])

    # Retrieve
    response = admin_api_client.get(detail_url)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == category_active.id

    # Update
    update_payload = {
        "name": "Updated Category",
        "slug": "updated-category",
        "is_active": False,
    }
    response = admin_api_client.put(detail_url, update_payload, format="json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["is_active"] == False

    # Delete
    response = admin_api_client.delete(detail_url)
    assert response.status_code == 204


@pytest.mark.django_db
def test_non_admin_cannot_access_admin_endpoints(api_client, user, category_active):
    api_client.force_authenticate(user=user)
    url = reverse("admin-category-list-create")
    response = api_client.get(url)
    assert response.status_code == 403
