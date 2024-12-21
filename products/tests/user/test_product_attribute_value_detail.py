from django.test import TestCase
from django.urls import reverse

from products.models import ProductAttribute, ProductAttributeValue


class ProductAttributeValueDetailViewTest(TestCase):
    def setUp(self):
        self.attr_color = ProductAttribute.objects.create(
            name="Color", description="Color attribute"
        )
        self.attr_size = ProductAttribute.objects.create(
            name="Size", description="Size attribute"
        )

        self.color_value_red = ProductAttributeValue.objects.create(
            product_attribute=self.attr_color, attribute_value="Red"
        )
        self.color_value_blue = ProductAttributeValue.objects.create(
            product_attribute=self.attr_color, attribute_value="Blue"
        )

        self.size_value_small = ProductAttributeValue.objects.create(
            product_attribute=self.attr_size, attribute_value="Small"
        )

        self.existing_url = reverse(
            "product-attribute-value-detail",
            kwargs={
                "attribute_id": self.attr_color.id,
                "value_id": self.color_value_red.id,
            },
        )

        self.non_existent_attribute_url = reverse(
            "product-attribute-value-detail",
            kwargs={"attribute_id": 9999, "value_id": self.color_value_red.id},
        )

        self.non_existent_value_url = reverse(
            "product-attribute-value-detail",
            kwargs={"attribute_id": self.attr_color.id, "value_id": 9999},
        )

        self.mismatched_attribute_value_url = reverse(
            "product-attribute-value-detail",
            kwargs={
                "attribute_id": self.attr_size.id,
                "value_id": self.color_value_red.id,
            },
        )

    def test_get_existing_attribute_value(self):
        response = self.client.get(self.existing_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("attribute_value", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertEqual(data["id"], self.color_value_red.id)
        self.assertEqual(data["attribute_value"], "Red")

    def test_non_existent_attribute(self):
        response = self.client.get(self.non_existent_attribute_url)
        self.assertEqual(response.status_code, 404)

    def test_non_existent_value(self):
        response = self.client.get(self.non_existent_value_url)
        self.assertEqual(response.status_code, 404)

    def test_mismatched_attribute_value(self):
        # Trying to get a value from another attribute should fail
        response = self.client.get(self.mismatched_attribute_value_url)
        self.assertEqual(response.status_code, 404)

    def test_field_types_in_response(self):
        response = self.client.get(self.existing_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data["id"], int)
        self.assertIsInstance(data["attribute_value"], str)
        self.assertIsInstance(data["created_at"], str)
        self.assertIsInstance(data["updated_at"], str)
