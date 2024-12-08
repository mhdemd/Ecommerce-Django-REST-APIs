import io
import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from categories.models import Category
from products.models import Media, Product

# Temporary media root for testing
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media")

# Get User model
User = get_user_model()


def generate_image_file(name="test_image.jpg"):
    """Generate a valid image file for testing."""
    file = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type="image/jpeg")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AdminProductMediaListCreateViewTest(TestCase):
    def setUp(self):
        # Clear all data
        Product.objects.all().delete()
        Media.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        # Validate cleanup
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Media.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
        self.assertEqual(Brand.objects.count(), 0)

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
        self.media1 = Media.objects.create(
            product=self.product,
            image=generate_image_file("test_image1.jpg"),
            is_feature=True,
            ordering=1,
        )
        self.media2 = Media.objects.create(
            product=self.product,
            image=generate_image_file("test_image2.jpg"),
            is_feature=False,
            ordering=2,
        )

        # Validate setup
        self.assertEqual(Media.objects.count(), 2)

        self.url = reverse(
            "admin-product-media-list-create", kwargs={"id": self.product.id}
        )

    def tearDown(self):
        # Remove all files and folders in the test media directory after each test
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    def test_get_media_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate response
        data = response.json()
        print("Response Data:", data)  # Debugging
        self.assertEqual(len(data["results"]), 2)  # Ensure only 2 media exist
        for media_item in data["results"]:
            self.assertEqual(
                media_item["product"], self.product.id
            )  # Validate product ID

    def test_post_media_as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        payload = {
            "product": self.product.id,  # Add product field
            "image": generate_image_file("new_image.jpg"),  # Valid image
            "is_feature": False,
            "ordering": 3,
        }
        response = self.client.post(self.url, payload, format="multipart")
        print(response.json())  # Debugging validation errors
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Media.objects.filter(product=self.product).count(), 3)
