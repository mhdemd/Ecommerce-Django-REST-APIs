from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from products.models.attribute import ProductType

User = get_user_model()


@override_settings(MEDIA_ROOT="test_media_root")
class AdminProductTypeListCreateViewTest(TestCase):
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

        # Create Product Types
        self.product_type = ProductType.objects.create(name="Type 1", slug="type-1")

        self.url = reverse("admin-product-type-list-create")

    def tearDown(self):
        ProductType.objects.all().delete()

    def test_get_product_types_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response structure
        data = response.json()
        self.assertIn("results", data)  # Ensure pagination structure exists
        self.assertEqual(len(data["results"]), 1)  # Only 1 product type should exist

        # Check the content of the first item
        self.assertEqual(data["results"][0]["name"], "Type 1")

    def test_get_product_types_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_type_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "name": "Type 2",
            "slug": "type-2",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductType.objects.count(), 2)
        self.assertEqual(ProductType.objects.last().name, "Type 2")

    def test_create_product_type_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "name": "Type 2",
            "slug": "type-2",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_type_with_invalid_data(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "name": "",
            "slug": "",
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProductType.objects.count(), 1)
