from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from products.models import Product

User = get_user_model()


class ProductListViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1", slug="category-1")
        self.brand = Brand.objects.create(name="Brand 1", slug="brand-1")

        self.product1 = Product.objects.create(
            web_id="prod-001",
            slug="product-one",
            name="Product One",
            description="This is the first product",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )
        self.product2 = Product.objects.create(
            web_id="prod-002",
            slug="product-two",
            name="Product Two",
            description="Second product description",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )

    def test_get_product_list_without_search(self):
        url = reverse("product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(response.json()[0]["name"], "Product One")

    def test_get_product_list_with_search(self):
        url = reverse("product-list")
        response = self.client.get(url, {"search": "first"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Product One")

    def test_get_product_list_no_match_search(self):
        url = reverse("product-list")
        response = self.client.get(url, {"search": "unavailable"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)
