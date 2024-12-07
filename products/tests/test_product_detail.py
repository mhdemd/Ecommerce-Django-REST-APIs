from django.test import TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from products.models import Product


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1", slug="category-1")
        self.brand = Brand.objects.create(name="Brand 1", slug="brand-1")

        self.active_product = Product.objects.create(
            web_id="prod-001",
            slug="product-one",
            name="Product One",
            description="First product description",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )

        self.inactive_product = Product.objects.create(
            web_id="prod-002",
            slug="product-two",
            name="Product Two",
            description="Second product description",
            brand=self.brand,
            category=self.category,
            is_active=False,
        )

        self.detail_url = reverse(
            "product-detail", kwargs={"pk": self.active_product.id}
        )
        self.non_existent_url = reverse(
            "product-detail", kwargs={"pk": 9999}
        )  # Non-existent

    def test_get_existing_active_product(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Product One")
        self.assertEqual(data["brand_name"], "Brand 1")
        self.assertEqual(data["category_name"], "Category 1")
        # Ensure that expected fields exist
        self.assertIn("web_id", data)
        self.assertIn("description", data)

    def test_get_inactive_product(self):
        # Inactive product should not be returned since the queryset filters is_active=True
        url = reverse("product-detail", kwargs={"pk": self.inactive_product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_non_existent_product(self):
        response = self.client.get(self.non_existent_url)
        self.assertEqual(response.status_code, 404)

    def test_get_product_fields_types(self):
        # Check field types to ensure correct data serialization
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data["id"], int)
        self.assertIsInstance(data["name"], str)
        self.assertIsInstance(data["brand"], int)
        self.assertIsInstance(data["category"], int)
        self.assertIsInstance(data["brand_name"], str)
        self.assertIsInstance(data["category_name"], str)
