import pytest
from django.urls import reverse

from brands.models import Brand


@pytest.mark.django_db
class TestAdminBrandEndpoints:
    def test_create_brand_admin(self, authenticated_admin_client):
        data = {
            "name": "Admin Brand",
            "slug": "admin-brand",
            "description": "Admin created brand",
        }
        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.post(url, data=data, format="json")
        assert response.status_code == 201
        assert Brand.objects.filter(name="Admin Brand").exists()

    def test_create_brand_admin_unauthenticated(self, api_client):
        data = {"name": "Brand X", "slug": "brand-x"}
        url = reverse("admin-brand-list-create")
        response = api_client.post(url, data=data, format="json")
        assert response.status_code == 401

    def test_update_brand_admin(self, authenticated_admin_client):
        brand = Brand.objects.create(name="Brand Old", slug="brand-old")
        data = {"name": "Brand New", "slug": "brand-new"}
        url = reverse("admin-brand-detail", args=[brand.id])
        response = authenticated_admin_client.patch(url, data=data, format="json")
        assert response.status_code == 200
        brand.refresh_from_db()
        assert brand.name == "Brand New"

    def test_delete_brand_admin(self, authenticated_admin_client):
        brand = Brand.objects.create(name="Brand To Delete", slug="brand-to-delete")
        url = reverse("admin-brand-detail", args=[brand.id])
        response = authenticated_admin_client.delete(url)
        assert response.status_code == 204
        assert not Brand.objects.filter(id=brand.id).exists()

    def test_detail_brand_admin(self, authenticated_admin_client):
        brand = Brand.objects.create(name="Detail Brand", slug="detail-brand")
        url = reverse("admin-brand-detail", args=[brand.id])
        response = authenticated_admin_client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Detail Brand"

    def test_filter_brands_by_name_admin(self, authenticated_admin_client):
        Brand.objects.create(name="Brand A", slug="brand-a")
        Brand.objects.create(name="Brand B", slug="brand-b")

        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.get(url, {"name": "Brand A"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Brand A"

    def test_filter_brands_by_slug_admin(self, authenticated_admin_client):
        Brand.objects.create(name="Brand A", slug="brand-a")
        Brand.objects.create(name="Brand B", slug="brand-b")

        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.get(url, {"slug": "brand-b"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["slug"] == "brand-b"

    def test_search_brands_by_name_admin(self, authenticated_admin_client):
        Brand.objects.create(name="Awesome Brand", slug="awesome-brand")
        Brand.objects.create(name="Another Brand", slug="another-brand")

        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.get(url, {"search": "Awesome"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Awesome Brand"

    def test_search_brands_by_description_admin(self, authenticated_admin_client):
        Brand.objects.create(
            name="Brand A", slug="brand-a", description="Great quality"
        )
        Brand.objects.create(name="Brand B", slug="brand-b", description="Affordable")

        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.get(url, {"search": "quality"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["description"] == "Great quality"

    def test_sort_brands_by_name_admin(self, authenticated_admin_client):
        Brand.objects.create(name="Zeta Brand", slug="zeta-brand")
        Brand.objects.create(name="Alpha Brand", slug="alpha-brand")

        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.get(url, {"ordering": "name"})
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["name"] == "Alpha Brand"
        assert data["results"][1]["name"] == "Zeta Brand"

    def test_sort_brands_by_created_at_admin(self, authenticated_admin_client):
        Brand.objects.create(name="Old Brand", slug="old-brand")
        Brand.objects.create(name="New Brand", slug="new-brand")

        url = reverse("admin-brand-list-create")
        response = authenticated_admin_client.get(url, {"ordering": "-created_at"})
        assert response.status_code == 200
        data = response.json()
        assert data["results"][0]["name"] == "New Brand"
        assert data["results"][1]["name"] == "Old Brand"

    def test_unauthorized_user_cannot_access_admin_list(
        self, authenticated_user_client
    ):
        url = reverse("admin-brand-list-create")
        response = authenticated_user_client.get(url)
        assert response.status_code == 403  # Expected for authenticated non-admin users
