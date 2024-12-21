from django.test import TestCase
from django.urls import reverse

from products.models import ProductType


class ProductTypeDetailViewTest(TestCase):
    def setUp(self):
        self.ptype1 = ProductType.objects.create(name="Type One", slug="type-one")
        self.ptype2 = ProductType.objects.create(name="Type Two", slug="type-two")

        self.existing_url = reverse(
            "product-type-detail", kwargs={"pk": self.ptype1.id}
        )
        self.non_existent_url = reverse("product-type-detail", kwargs={"pk": 9999})

    def test_get_existing_product_type(self):
        response = self.client.get(self.existing_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("name", data)
        self.assertIn("slug", data)
        self.assertEqual(data["id"], self.ptype1.id)
        self.assertEqual(data["name"], "Type One")
        self.assertEqual(data["slug"], "type-one")

    def test_get_non_existent_product_type(self):
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, 404)

    def test_field_types_in_response(self):
        response = self.client.get(self.existing_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data["id"], int)
        self.assertIsInstance(data["name"], str)
        self.assertIsInstance(data["slug"], str)
