from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from products.models import Product, ProductInventory, ProductType


class ProductInventoryListViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1", slug="category-1")
        self.brand = Brand.objects.create(name="Brand 1", slug="brand-1")
        self.product_type = ProductType.objects.create(name="Type 1", slug="type-1")

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

        # Create some inventories for the active product
        self.inventory1 = ProductInventory.objects.create(
            sku="SKU-001",
            upc="UPC-001",
            product_type=self.product_type,
            product=self.active_product,
            stock=100,
            is_active=True,
            retail_price=Decimal("49.99"),
            store_price=Decimal("45.00"),
            sale_price=Decimal("39.99"),
            weight=Decimal("1.2"),
        )

        self.inventory2 = ProductInventory.objects.create(
            sku="SKU-002",
            upc="UPC-002",
            product_type=self.product_type,
            product=self.active_product,
            stock=50,
            is_active=True,
            retail_price=Decimal("59.99"),
            store_price=Decimal("55.00"),
            sale_price=Decimal("49.99"),
            weight=Decimal("1.5"),
        )

        self.url_active_product = reverse(
            "product-inventory-list", kwargs={"pk": self.active_product.id}
        )
        self.url_inactive_product = reverse(
            "product-inventory-list", kwargs={"pk": self.inactive_product.id}
        )
        self.url_non_existent_product = reverse(
            "product-inventory-list", kwargs={"pk": 9999}
        )

    def test_get_inventory_for_active_product(self):
        response = self.client.get(self.url_active_product)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["id"], self.inventory1.id)
        self.assertEqual(data["results"][0]["sku"], "SKU-001")
        self.assertEqual(data["results"][1]["id"], self.inventory2.id)
        self.assertEqual(data["results"][1]["sku"], "SKU-002")

    def test_get_inventory_for_inactive_product(self):
        response = self.client.get(self.url_inactive_product)
        self.assertEqual(response.status_code, 404)

    def test_get_inventory_for_non_existent_product(self):
        response = self.client.get(self.url_non_existent_product)
        self.assertEqual(response.status_code, 404)

    def test_get_inventory_for_product_with_no_inventory(self):
        product_no_inventory = Product.objects.create(
            web_id="prod-003",
            slug="product-three",
            name="Product Three",
            description="Third product description",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )
        url_no_inventory = reverse(
            "product-inventory-list", kwargs={"pk": product_no_inventory.id}
        )
        response = self.client.get(url_no_inventory)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)

    def test_field_types_in_response(self):
        response = self.client.get(self.url_active_product)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        item = data["results"][0]
        self.assertIn("id", item)
        self.assertIn("sku", item)
        self.assertIn("upc", item)
        self.assertIn("stock", item)
        self.assertIn("retail_price", item)
        self.assertIn("store_price", item)
        self.assertIn("sale_price", item)
        self.assertIn("weight", item)
        self.assertIn("is_active", item)
        self.assertIsInstance(item["id"], int)
        self.assertIsInstance(item["sku"], str)
        self.assertIsInstance(item["upc"], str)
        self.assertIsInstance(item["stock"], int)
        self.assertIsInstance(item["retail_price"], str)
        self.assertIsInstance(item["store_price"], str)
        # Decimal fields are returned as strings
        self.assertIsInstance(item["sale_price"], (str, type(None)))
        self.assertIsInstance(item["weight"], str)
        self.assertIsInstance(item["is_active"], bool)
