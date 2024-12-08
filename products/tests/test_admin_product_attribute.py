from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from products.models.attribute import ProductAttribute

User = get_user_model()


@override_settings(MEDIA_ROOT="test_media_root")
class AdminProductAttributeListCreateViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(username="user", password="password")
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword"
        )

        # Generate tokens
        self.admin_token = str(AccessToken.for_user(self.admin_user))
        self.user_token = str(AccessToken.for_user(self.user))

        # Create Product Attribute
        self.product_attribute = ProductAttribute.objects.create(
            name="Color",
            description="Defines the color of the product",
        )

        self.url = reverse("admin-product-attribute-list-create")

    def tearDown(self):
        ProductAttribute.objects.all().delete()

    def test_get_product_attributes_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("results", data)  # Pagination
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "Color")

    def test_get_product_attributes_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_attribute_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "name": "Size",
            "description": "Defines the size of the product",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductAttribute.objects.count(), 2)
        self.assertEqual(ProductAttribute.objects.last().name, "Size")

    def test_create_product_attribute_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "name": "Size",
            "description": "Defines the size of the product",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_attribute_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "name": "",
            "description": "",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProductAttribute.objects.count(), 1)
