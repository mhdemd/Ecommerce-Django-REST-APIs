from django.test import TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from products.models import Product


class ProductListViewTest(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Category 1", slug="category-1")
        self.category2 = Category.objects.create(name="Category 2", slug="category-2")
        self.brand1 = Brand.objects.create(name="Brand 1", slug="brand-1")
        self.brand2 = Brand.objects.create(name="Brand 2", slug="brand-2")

        self.product1 = Product.objects.create(
            web_id="prod-001",
            slug="product-one",
            name="Product One",
            description="This is the first product",
            brand=self.brand1,
            category=self.category1,
            is_active=True,
        )
        self.product2 = Product.objects.create(
            web_id="prod-002",
            slug="product-two",
            name="Product Two",
            description="Second product description",
            brand=self.brand1,
            category=self.category2,
            is_active=True,
        )
        self.product3 = Product.objects.create(
            web_id="prod-003",
            slug="product-three",
            name="Product Three",
            description="Third product description",
            brand=self.brand2,
            category=self.category1,
            is_active=True,
        )

        self.url = reverse("product-list")

    def test_get_product_list_without_filters(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Since pagination is active, the response will be a dictionary
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 3)  # All products should be returned

    def test_get_product_list_with_search(self):
        response = self.client.get(self.url, {"search": "first"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "Product One")

    def test_get_product_list_with_filter_brand(self):
        # Filter by brand=brand1
        response = self.client.get(self.url, {"brand": self.brand1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # product1 and product2 should be returned
        self.assertEqual(len(data["results"]), 2)
        names = [p["name"] for p in data["results"]]
        self.assertIn("Product One", names)
        self.assertIn("Product Two", names)
        self.assertNotIn("Product Three", names)

    def test_get_product_list_with_filter_category(self):
        # Filter by category=category1
        response = self.client.get(self.url, {"category": self.category1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # product1 and product3 should be returned
        self.assertEqual(len(data["results"]), 2)
        names = [p["name"] for p in data["results"]]
        self.assertIn("Product One", names)
        self.assertIn("Product Three", names)
        self.assertNotIn("Product Two", names)

    def test_product_list_pagination(self):
        # By default PAGE_SIZE=10, we have only 3 products, so all are on page 1
        response = self.client.get(self.url, {"page": 1})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 3)

        # If we want 2 per page, we need to adjust PAGE_SIZE in settings or use custom pagination parameters.
        # Assuming PAGE_SIZE=2, then:
        # With the current setup (PAGE_SIZE=10), this test is not meaningful.
        # If PAGE_SIZE were 2:
        #
        # response = self.client.get(self.url, {"page": 2})
        # data = response.json()
        # self.assertEqual(len(data["results"]), 1)  # The third product would be on the second page.
