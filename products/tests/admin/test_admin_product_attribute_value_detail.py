from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from products.models.attribute import ProductAttribute, ProductAttributeValue

User = get_user_model()


@override_settings(MEDIA_ROOT="test_media_root")
class AdminProductAttributeValueDetailViewTest(TestCase):
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

        # Create Product Attribute and Values
        self.product_attribute = ProductAttribute.objects.create(
            name="Color",
            description="Defines the color of the product",
        )
        self.attribute_value = ProductAttributeValue.objects.create(
            product_attribute=self.product_attribute,
            attribute_value="Red",
        )

        self.url = reverse(
            "admin-product-attribute-value-detail",
            kwargs={
                "attribute_id": self.product_attribute.id,
                "pk": self.attribute_value.id,
            },
        )

    def tearDown(self):
        ProductAttributeValue.objects.all().delete()
        ProductAttribute.objects.all().delete()

    def test_get_attribute_value_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["attribute_value"], "Red")

    def test_get_attribute_value_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_attribute_value_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {"attribute_value": "Blue"}
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.attribute_value.refresh_from_db()
        self.assertEqual(self.attribute_value.attribute_value, "Blue")

    def test_update_attribute_value_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {"attribute_value": "Blue"}
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_attribute_value_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            ProductAttributeValue.objects.filter(id=self.attribute_value.id).count(),
            0,
        )

    def test_delete_attribute_value_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
