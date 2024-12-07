from django.test import TestCase, override_settings
from django.urls import reverse

from products.models import ProductAttribute


@override_settings(
    REST_FRAMEWORK={"DEFAULT_THROTTLE_CLASSES": [], "DEFAULT_THROTTLE_RATES": {}}
)
class ProductAttributeDetailViewTest(TestCase):
    def setUp(self):
        self.attr1 = ProductAttribute.objects.create(
            name="Color", description="The color attribute"
        )
        self.attr2 = ProductAttribute.objects.create(
            name="Size", description="The size attribute"
        )

        self.existing_url = reverse(
            "product-attribute-detail", kwargs={"pk": self.attr1.id}
        )
        self.non_existent_url = reverse("product-attribute-detail", kwargs={"pk": 9999})

    def test_get_existing_product_attribute(self):
        response = self.client.get(self.existing_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("description", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["id"], self.attr1.id)
        self.assertEqual(data["name"], "Color")
        self.assertEqual(data["description"], "The color attribute")

    def test_get_non_existent_product_attribute(self):
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, 404)

    def test_field_types_in_response(self):
        response = self.client.get(self.existing_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data["id"], int)
        self.assertIsInstance(data["name"], str)
        self.assertIsInstance(data["description"], str)
        self.assertIsInstance(data["created_at"], str)
        self.assertIsInstance(data["updated_at"], str)
