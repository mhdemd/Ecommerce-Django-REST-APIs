import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestUserCategoryEndpoints:
    def test_user_can_list_active_categories(
        self, api_client, category_active, category_inactive
    ):
        url = reverse("category-list")
        response = api_client.get(url)
        assert response.status_code == 200

        ids = [c["id"] for c in response.json()["results"]]
        assert category_active.id in ids
        assert category_inactive.id not in ids

    def test_user_can_get_active_category_detail(self, api_client, category_active):
        url = reverse("category-detail", args=[category_active.id])
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category_active.id
        assert data["name"] == "Active Category"

    def test_user_cannot_get_inactive_category_detail(
        self, api_client, category_inactive
    ):
        url = reverse("category-detail", args=[category_inactive.id])
        response = api_client.get(url)
        assert response.status_code == 404

    def test_user_can_filter_categories_by_name(
        self, api_client, category_active, category_inactive
    ):
        url = reverse("category-list")
        filter_url = f"{url}?name={category_active.name}"
        response = api_client.get(filter_url)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == category_active.id

    @pytest.mark.django_db
    def test_user_can_sort_categories_by_name(
        self, api_client, category_active, category_inactive
    ):
        # Ensure both categories are active and have distinct names for sorting
        category_active.name = "A Category"
        category_active.is_active = True
        category_active.save()

        category_inactive.name = "B Category"
        category_inactive.is_active = True  # Ensure this category is active
        category_inactive.save()

        url = reverse("category-list")
        sort_url = f"{url}?ordering=name"
        response = api_client.get(sort_url)
        assert response.status_code == 200

        results = response.json()["results"]

        # Ensure we have at least two results to test sorting
        assert (
            len(results) >= 2
        ), f"Expected at least 2 results, but got {len(results)}: {results}"
        assert results[0]["name"] <= results[1]["name"]

    def test_user_can_search_categories_by_name(
        self, api_client, category_active, category_inactive
    ):
        url = reverse("category-list")
        search_url = f"{url}?search={category_active.name}"
        response = api_client.get(search_url)
        assert response.status_code == 200

        results = response.json()["results"]
        assert len(results) == 1
        assert results[0]["id"] == category_active.id
