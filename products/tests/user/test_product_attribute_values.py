from django.test import TestCase
from django.urls import reverse

from products.models import ProductAttribute, ProductAttributeValue


class ProductAttributeValueListViewTest(TestCase):
    def setUp(self):
        self.attr_color = ProductAttribute.objects.create(
            name="Color", description="Color attribute"
        )
        self.attr_size = ProductAttribute.objects.create(
            name="Size", description="Size attribute"
        )

        self.color_value1 = ProductAttributeValue.objects.create(
            product_attribute=self.attr_color, attribute_value="Red"
        )
        self.color_value2 = ProductAttributeValue.objects.create(
            product_attribute=self.attr_color, attribute_value="Blue"
        )

        self.size_value1 = ProductAttributeValue.objects.create(
            product_attribute=self.attr_size, attribute_value="Small"
        )

        self.color_url = reverse(
            "product-attribute-value-list", kwargs={"attribute_id": self.attr_color.id}
        )
        self.size_url = reverse(
            "product-attribute-value-list", kwargs={"attribute_id": self.attr_size.id}
        )
        self.non_existent_url = reverse(
            "product-attribute-value-list", kwargs={"attribute_id": 9999}
        )

    def test_get_values_for_existing_attribute(self):
        response = self.client.get(self.color_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        values = [item["attribute_value"] for item in data["results"]]
        self.assertIn("Red", values)
        self.assertIn("Blue", values)

    def test_get_values_for_attribute_with_one_value(self):
        response = self.client.get(self.size_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["attribute_value"], "Small")

    def test_get_values_for_non_existent_attribute(self):
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, 404)

    def test_get_values_for_attribute_with_no_values(self):
        # Create a new attribute with no values
        attr_empty = ProductAttribute.objects.create(
            name="Material", description="Material attribute"
        )
        url_empty = reverse(
            "product-attribute-value-list", kwargs={"attribute_id": attr_empty.id}
        )
        response = self.client.get(url_empty)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)

    def test_field_types_in_response(self):
        response = self.client.get(self.color_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 1)
        item = data["results"][0]
        self.assertIn("id", item)
        self.assertIn("attribute_value", item)

        self.assertIsInstance(item["id"], int)
        self.assertIsInstance(item["attribute_value"], str)
