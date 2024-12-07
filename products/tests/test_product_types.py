from django.test import TestCase
from django.urls import reverse

from products.models import ProductType


class ProductTypeListViewTest(TestCase):
    def setUp(self):
        self.url = reverse("product-type-list")
        # Creating a few product types
        self.ptype1 = ProductType.objects.create(name="Type One", slug="type-one")
        self.ptype2 = ProductType.objects.create(name="Type Two", slug="type-two")

    def test_get_product_type_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        # Check that the fields are present
        self.assertIn("id", data["results"][0])
        self.assertIn("name", data["results"][0])
        self.assertIn("slug", data["results"][0])

    def test_get_product_type_list_empty(self):
        ProductType.objects.all().delete()
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
        self.assertIsInstance(item["slug"], str)
