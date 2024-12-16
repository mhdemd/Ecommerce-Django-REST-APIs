import pytest
from brand.models import Brand
from django.urls import reverse


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
        assert response.status_code == 403  # Forbidden برای کاربر غیر احراز هویت شده

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
