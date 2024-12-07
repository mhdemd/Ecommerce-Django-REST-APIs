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
        # چون پجینیشن فعال است، پاسخ یک دیکشنری خواهد بود
        data = response.json()
        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 3)  # همه محصولات برگردانده می‌شوند

    def test_get_product_list_with_search(self):
        response = self.client.get(self.url, {"search": "first"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "Product One")

    def test_get_product_list_with_filter_brand(self):
        # فقط محصولاتی که brand=brand1 دارند
        response = self.client.get(self.url, {"brand": self.brand1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # انتظار می‌رود product1, product2 برگردند
        self.assertEqual(len(data["results"]), 2)
        names = [p["name"] for p in data["results"]]
        self.assertIn("Product One", names)
        self.assertIn("Product Two", names)
        self.assertNotIn("Product Three", names)

    def test_get_product_list_with_filter_category(self):
        # فقط محصولاتی که category=category1 دارند
        response = self.client.get(self.url, {"category": self.category1.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # انتظار می‌رود product1 و product3 برگردند
        self.assertEqual(len(data["results"]), 2)
        names = [p["name"] for p in data["results"]]
        self.assertIn("Product One", names)
        self.assertIn("Product Three", names)
        self.assertNotIn("Product Two", names)

    def test_product_list_pagination(self):
        # پیشفرض 10 تا در هر صفحه. ما سه محصول داریم پس همه تو صفحه 1 هستند
        response = self.client.get(self.url, {"page": 1})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 3)

        # اگر 2 تا در هر صفحه می‌خواهیم، باید PAGE_SIZE را در تنظیمات کم کنیم
        # یا از پارامترهای پجینیشن سفارشی استفاده کنیم.
        # فرض کنیم PAGE_SIZE=2 باشد، آنگاه:
        # با تنظیمات کنونی (در پاسخ اصلی PAGE_SIZE=10 است) این تست معنی ندارد
        # ولی اگر PAGE_SIZE را روی 2 بگذارید، تست زیر باید 2 محصول در page=1 بدهد
        # و 1 محصول در page=2
        #
        # این قسمت تست صرفاً برای نمایش است. اگر PAGE_SIZE=10 است تغییری نیاز نیست.
        #
        # response = self.client.get(self.url, {"page": 2})
        # data = response.json()
        # self.assertEqual(len(data['results']), 1)  # محصول سوم در صفحه دوم
