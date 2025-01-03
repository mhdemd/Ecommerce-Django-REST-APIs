import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from brands.models import Brand
from categories.models import Category
from products.models import Media, Product

TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media")


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductMediaListViewTest(TestCase):
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

        # Create some media for the active product
        self.image_file = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        self.media1 = Media.objects.create(
            product=self.active_product,
            image=self.image_file,
            is_feature=True,
            ordering=1,
        )
        self.media2 = Media.objects.create(
            product=self.active_product,
            image=self.image_file,
            is_feature=False,
            ordering=2,
        )

        self.url_active_product = reverse(
            "product-media-list", kwargs={"pk": self.active_product.id}
        )
        self.url_inactive_product = reverse(
            "product-media-list", kwargs={"pk": self.inactive_product.id}
        )
        self.url_non_existent_product = reverse(
            "product-media-list", kwargs={"pk": 9999}
        )

    def tearDown(self):
        # Remove all files and folders in the test media directory after each test
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    def test_get_media_for_active_product(self):
        response = self.client.get(self.url_active_product)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["id"], self.media1.id)
        self.assertEqual(data["results"][1]["id"], self.media2.id)

    def test_get_media_for_inactive_product(self):
        response = self.client.get(self.url_inactive_product)
        self.assertEqual(response.status_code, 404)

    def test_get_media_for_non_existent_product(self):
        response = self.client.get(self.url_non_existent_product)
        self.assertEqual(response.status_code, 404)

    def test_get_media_for_product_with_no_media(self):
        product_no_media = Product.objects.create(
            web_id="prod-003",
            slug="product-three",
            name="Product Three",
            description="Third product description",
            brand=self.brand,
            category=self.category,
            is_active=True,
        )
        url_no_media = reverse("product-media-list", kwargs={"pk": product_no_media.id})
        response = self.client.get(url_no_media)
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

        # Fields that are actually returned by the serializer
        item = data["results"][0]
        self.assertIn("id", item)
        self.assertIn("image", item)
        self.assertIn("ordering", item)

        # Check the data types of the returned fields
        self.assertIsInstance(item["id"], int)
        self.assertIsInstance(item["image"], str)
        self.assertIsInstance(item["ordering"], int)
