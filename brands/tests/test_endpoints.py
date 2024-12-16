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
