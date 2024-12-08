import os
import shutil

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from categories.models import Category
from products.models import Media, Product

User = get_user_model()

# Custom test media root
TEST_MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "test_media")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AdminProductMediaDetailViewTest(TestCase):
    def setUp(self):
        Media.objects.all().delete()
        Product.objects.all().delete()

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

        # Create media
        self.media = Media.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "test_image.jpg", b"file_content", content_type="image/jpeg"
            ),
            is_feature=True,
            ordering=1,
        )

        self.url = reverse(
            "admin-product-media-detail",
            kwargs={"product_id": self.product.id, "pk": self.media.id},
        )

    def tearDown(self):
        # Remove all files and folders in the test media directory after each test
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    def test_get_media_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.media.id)
        self.assertEqual(data["is_feature"], True)

    def test_get_media_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_media_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "is_feature": False,
            "ordering": 2,
        }
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.media.refresh_from_db()
        self.assertEqual(self.media.is_feature, False)
        self.assertEqual(self.media.ordering, 2)

    def test_update_media_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        payload = {
            "is_feature": False,
            "ordering": 2,
        }
        response = self.client.put(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_media_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Media.objects.filter(id=self.media.id).count(), 0)

    def test_delete_media_as_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
