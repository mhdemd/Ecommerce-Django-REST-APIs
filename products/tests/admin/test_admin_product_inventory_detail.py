from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from categories.models import Category
from products.models import Product, ProductInventory
from products.models.attribute import (
    ProductAttribute,
    ProductAttributeValue,
    ProductType,
)

User = get_user_model()

TEST_MEDIA_ROOT = "test_media_root"


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AdminProductInventoryDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(username="user", password="password")
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword"
        )

        # Generate tokens
        self.admin_token = str(AccessToken.for_user(self.admin_user))
        self.user_token = str(AccessToken.for_user(self.user))

        # Create related data
        self.category = Category.objects.create(name="Category 1", slug="category-1")
        self.brand = Brand.objects.create(name="Brand 1", slug="brand-1")
        self.product_type = ProductType.objects.create(name="Type 1", slug="type-1")

        # Create ProductAttribute and ProductAttributeValue
        self.product_attribute = ProductAttribute.objects.create(
            name="Color", description="Product Color"
        )
        self.attribute_value = ProductAttributeValue.objects.create(
            product_attribute=self.product_attribute, attribute_value="Red"
        )

        # Create a product
        self.product = Product.objects.create(
            web_id="prod-001",
            slug="product-one",
            name="Product One",
            description="First product description",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )

        # Create inventory
        self.inventory = ProductInventory.objects.create(
            sku="SKU001",
            upc="123456789012",
            product=self.product,
            product_type=self.product_type,
            stock=100,
            is_active=True,
            retail_price=99.99,
            store_price=89.99,
            weight=1.5,
        )
        self.inventory.attribute_values.add(self.attribute_value)

        self.url = reverse(
            "admin-product-inventory-detail", kwargs={"sku": self.inventory.sku}
        )

    def tearDown(self):
        ProductInventory.objects.all().delete()
        ProductAttributeValue.objects.all().delete()
        ProductAttribute.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        ProductType.objects.all().delete()

    def test_get_inventory_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["sku"], "SKU001")
        self.assertEqual(data["stock"], 100)

    def test_get_inventory_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_inventory_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "sku": self.inventory.sku,
            "upc": self.inventory.upc,
            "product": self.product.id,
            "product_type": self.product_type.id,
            "attribute_values": [self.attribute_value.id],
            "stock": 200,
            "is_active": False,
            "retail_price": 120.00,
            "store_price": 110.00,
            "sale_price": 105.00,
            "weight": 2.0,
        }
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.stock, 200)
        self.assertEqual(self.inventory.is_active, False)

    def test_update_inventory_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "sku": self.inventory.sku,
            "upc": self.inventory.upc,
            "product": self.product.id,
            "product_type": self.product_type.id,
            "attribute_values": [self.attribute_value.id],
            "stock": 200,
            "is_active": False,
            "retail_price": 120.00,
            "store_price": 110.00,
            "sale_price": 105.00,
            "weight": 2.0,
        }
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_inventory_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(
            ProductInventory.objects.filter(sku=self.inventory.sku).count(), 0
        )

    def test_delete_inventory_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
