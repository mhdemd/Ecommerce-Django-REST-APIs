# import pytest

# from brands.models import Brand


# @pytest.mark.django_db
# class TestAdminBrandEndpoints:
#     def test_create_brand_admin(self, authenticated_admin_client):
#         data = {
#             "name": "Admin Brand",
#             "slug": "admin-brand",
#             "description": "Admin created brand",
#         }
#         response = authenticated_admin_client.post(
#             "/admin/brands/", data=data, format="json"
#         )
#         assert response.status_code == 201
#         brand_id = response.json()["id"]
#         brand = Brand.objects.get(id=brand_id)
#         assert brand.name == "Admin Brand"

#     def test_create_brand_admin_unauthenticated(self, api_client):
#         data = {"name": "Brand X", "slug": "brand-x"}
#         response = api_client.post("/admin/brands/", data=data, format="json")
#         assert response.status_code == 403

#     def test_update_brand_admin(self, authenticated_admin_client):
#         brand = Brand.objects.create(name="Brand Old", slug="brand-old")
#         update_data = {"name": "Brand New", "slug": "brand-new"}
#         response = authenticated_admin_client.patch(
#             f"/admin/brands/{brand.id}/", data=update_data, format="json"
#         )
#         assert response.status_code == 200
#         brand.refresh_from_db()
#         assert brand.name == "Brand New"
#         assert brand.slug == "brand-new"

#     def test_delete_brand_admin(self, authenticated_admin_client):
#         brand = Brand.objects.create(name="Brand To Delete", slug="brand-to-delete")
#         response = authenticated_admin_client.delete(f"/admin/brands/{brand.id}/")
#         assert response.status_code == 204
#         assert Brand.objects.filter(id=brand.id).count() == 0

#     def test_detail_brand_admin(self, authenticated_admin_client):
#         brand = Brand.objects.create(name="Detail Brand", slug="detail-brand")
#         response = authenticated_admin_client.get(f"/admin/brands/{brand.id}/")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["name"] == "Detail Brand"
