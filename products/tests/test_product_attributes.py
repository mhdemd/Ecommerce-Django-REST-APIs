from django.test import TestCase
from django.urls import reverse

from products.models import ProductAttribute


class ProductAttributeListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("product-attribute-list")
        self.attr1 = ProductAttribute.objects.create(
            name="Color", description="Product color"
        )
        self.attr2 = ProductAttribute.objects.create(
            name="Size", description="Product size"
        )

    def test_get_product_attribute_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertIn("id", data["results"][0])
        self.assertIn("name", data["results"][0])
        self.assertIn("description", data["results"][0])
        self.assertIn("created_at", data["results"][0])
        self.assertIn("updated_at", data["results"][0])

    def test_get_product_attribute_list_empty(self):
        ProductAttribute.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)

    def test_field_types_in_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        item = data["results"][0]
        self.assertIsInstance(item["id"], int)
        self.assertIsInstance(item["name"], str)
        self.assertIsInstance(item["description"], str)
        self.assertIsInstance(item["created_at"], str)
        self.assertIsInstance(item["updated_at"], str)
