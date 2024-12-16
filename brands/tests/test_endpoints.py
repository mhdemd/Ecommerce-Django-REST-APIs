import pytest
from django.urls import reverse

from brands.models import Brand


@pytest.mark.django_db
class TestPublicBrandEndpoints:
    def test_list_brands(self, api_client):
        Brand.objects.create(name="Brand A", slug="brand-a")
        Brand.objects.create(name="Brand B", slug="brand-b")

        url = reverse("brand-list")
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["results"][0]["name"] in ["Brand A", "Brand B"]
        assert data["results"][1]["name"] in ["Brand A", "Brand B"]

    def test_retrieve_brand(self, api_client):
        brand = Brand.objects.create(name="Brand C", slug="brand-c")
        url = reverse("brand-detail", args=[brand.id])
        response = api_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Brand C"
        assert data["slug"] == "brand-c"

    def test_retrieve_non_existing_brand(self, api_client):
        url = reverse("brand-detail", args=[99999])
        response = api_client.get(url)
        assert response.status_code == 404

    def test_filter_brands_by_name(self, api_client):
        Brand.objects.create(name="Brand A", slug="brand-a")
        Brand.objects.create(name="Brand B", slug="brand-b")

        url = reverse("brand-list")
        response = api_client.get(url, {"name": "Brand A"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Brand A"

    def test_filter_brands_by_slug(self, api_client):
        Brand.objects.create(name="Brand A", slug="brand-a")
        Brand.objects.create(name="Brand B", slug="brand-b")

        url = reverse("brand-list")
        response = api_client.get(url, {"slug": "brand-b"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["slug"] == "brand-b"

    def test_search_brands_by_name(self, api_client):
        Brand.objects.create(name="Awesome Brand", slug="awesome-brand")
        Brand.objects.create(name="Another Brand", slug="another-brand")

        url = reverse("brand-list")
        response = api_client.get(url, {"search": "Awesome"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Awesome Brand"

    def test_search_brands_by_description(self, api_client):
        Brand.objects.create(
            name="Brand A", slug="brand-a", description="Great quality"
        )
        Brand.objects.create(name="Brand B", slug="brand-b", description="Affordable")

        url = reverse("brand-list")
        response = api_client.get(url, {"search": "quality"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["description"] == "Great quality"

    def test_sort_brands_by_name(self, api_client):
        Brand.objects.create(name="Zeta Brand", slug="zeta-brand")
        Brand.objects.create(name="Alpha Brand", slug="alpha-brand")

        url = reverse("brand-list")
        response = api_client.get(url, {"ordering": "name"})
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["name"] == "Alpha Brand"
        assert data["results"][1]["name"] == "Zeta Brand"

    def test_sort_brands_by_created_at(self, api_client):
        Brand.objects.create(name="Old Brand", slug="old-brand")
        Brand.objects.create(name="New Brand", slug="new-brand")

        url = reverse("brand-list")
        response = api_client.get(url, {"ordering": "-created_at"})
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["name"] == "New Brand"
        assert data["results"][1]["name"] == "Old Brand"
