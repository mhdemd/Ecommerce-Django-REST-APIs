import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAdminCategoryEndpoints:
    def test_admin_can_list_all_categories(
        self, admin_api_client, category_active, category_inactive
    ):
        # Test listing all categories
        url = reverse("admin-category-list-create")
        response = admin_api_client.get(url)
        assert response.status_code == 200
        ids = [c["id"] for c in response.json()["results"]]
        assert category_active.id in ids
        assert category_inactive.id in ids

    def test_admin_can_list_categories_with_search_filter_ordering(
        self, admin_api_client, category_active, category_inactive
    ):
        # Ensure unique names for the test
        category_active.name = "Books"
        category_active.save()
        category_inactive.name = "Electronics"
        category_inactive.save()

        url = reverse("admin-category-list-create")

        # Test search functionality
        search_url = f"{url}?search={category_active.name}"
        response = admin_api_client.get(search_url)
        assert response.status_code == 200
        results = response.json()["results"]

        # Debugging assertion
        assert (
            len(results) == 1
        ), f"Expected 1 result, but got {len(results)}: {results}"
        assert results[0]["id"] == category_active.id

        # Test filter functionality
        filter_url = f"{url}?is_active=True"
        response = admin_api_client.get(filter_url)
        assert response.status_code == 200
        results = response.json()["results"]
        assert all(c["is_active"] for c in results)

        # Test ordering functionality
        ordering_url = f"{url}?ordering=-created_at"
        response = admin_api_client.get(ordering_url)
        assert response.status_code == 200
        results = response.json()["results"]
        assert results[0]["created_at"] >= results[1]["created_at"]

    def test_admin_can_create_category(self, admin_api_client, category_active):
        # Test creating a new category
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
        assert data["is_active"] is True

    def test_admin_can_retrieve_update_delete_category(
        self, admin_api_client, category_active
    ):
        detail_url = reverse("admin-category-detail", args=[category_active.id])

        # Test retrieving a category
        response = admin_api_client.get(detail_url)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_active.id

        # Test updating a category
        update_payload = {
            "name": "Updated Category",
            "slug": "updated-category",
            "is_active": False,
        }
        response = admin_api_client.put(detail_url, update_payload, format="json")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Category"
        assert data["is_active"] is False

        # Test deleting a category
        response = admin_api_client.delete(detail_url)
        assert response.status_code == 204

    def test_non_admin_cannot_access_admin_endpoints(
        self, api_client, user, category_active
    ):
        # Test that a non-admin user cannot access admin endpoints
        api_client.force_authenticate(user=user)
        url = reverse("admin-category-list-create")
        response = api_client.get(url)
        assert response.status_code == 403
