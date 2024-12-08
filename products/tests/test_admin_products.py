from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from categories.models import Category
from products.models import Product

User = get_user_model()


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 10,
    }
)
class AdminProductListCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user = User.objects.create_user(username="user", password="password")
        cls.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword"
        )

        # Generate tokens
        cls.admin_token = str(AccessToken.for_user(cls.admin_user))
        cls.user_token = str(AccessToken.for_user(cls.user))

        # Create related data
        cls.category = Category.objects.create(name="Category 1", slug="category-1")
        cls.brand = Brand.objects.create(name="Brand 1", slug="brand-1")

        # Create a product
        cls.product = Product.objects.create(
            web_id="prod-001",
            slug="product-one",
            name="Product One",
            description="First product description",
            brand=cls.brand,
            category=cls.category,
            is_active=True,
        )

        cls.url = reverse("admin-product-list-create")

    def setUp(self):
        self.client = APIClient()
        # Ensure only one product exists
        Product.objects.all().delete()
        self.product = Product.objects.create(
            web_id="prod-001",
            slug="product-one",
            name="Product One",
            description="First product description",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )
        print(
            f"Number of products in setUp: {Product.objects.count()}"
        )  # Should print 1

    def test_get_products_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Access the 'results' key
        results = data.get("results", [])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Product One")

    def test_get_products_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_product_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "web_id": "prod-002",
            "slug": "product-two",
            "name": "Product Two",
            "description": "Second product description",
            "brand": self.brand.id,
            "category": self.category.id,
            "is_active": True,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.last().name, "Product Two")

    def test_post_product_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "web_id": "prod-002",
            "slug": "product-two",
            "name": "Product Two",
            "description": "Second product description",
            "brand": self.brand.id,
            "category": self.category.id,
            "is_active": True,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_product_with_invalid_data_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "web_id": "",
            "slug": "",
            "name": "",
            "description": "",
            "brand": self.brand.id,
            "category": self.category.id,
            "is_active": True,
        }
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
