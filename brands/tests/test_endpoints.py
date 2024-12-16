import pytest

from brands.models import Brand


@pytest.mark.django_db
class TestPublicBrandEndpoints:
    def test_list_brands(self, api_client):
        Brand.objects.create(name="Brand A", slug="brand-a")
        Brand.objects.create(name="Brand B", slug="brand-b")

        response = api_client.get("/brands/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["Brand A", "Brand B"]
        assert data[1]["name"] in ["Brand A", "Brand B"]

    def test_retrieve_brand(self, api_client):
        brand = Brand.objects.create(name="Brand C", slug="brand-c")
        response = api_client.get(f"/brands/{brand.id}/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Brand C"
        assert data["slug"] == "brand-c"

    def test_retrieve_non_existing_brand(self, api_client):
        response = api_client.get("/brands/99999/")
        assert response.status_code == 404
