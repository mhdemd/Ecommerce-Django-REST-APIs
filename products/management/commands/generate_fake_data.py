import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from brands.models import Brand
from categories.models import Category
from products.models import Media, Product, ProductInventory
from reviews.models import ProductReview
from wishlist.models import Wishlist

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Generate fake data for the e-commerce project"

    def handle(self, *args, **options):
        self.stdout.write("Generating fake data...")

        # Create Users
        for _ in range(20):
            User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="password123",
                is_active=True,
            )

        # Create Brands
        brands = []
        for _ in range(10):
            brand = Brand.objects.create(
                name=fake.company(),
                slug=fake.slug(),
                description=fake.text(),
                logo=fake.image_url(),
            )
            brands.append(brand)

        # Create Categories
        categories = []
        for _ in range(5):
            category = Category.objects.create(
                name=fake.word(),
                slug=fake.slug(),
                is_active=True,
            )
            categories.append(category)

        # Create Products
        products = []
        for _ in range(50):
            product = Product.objects.create(
                web_id=fake.unique.uuid4(),
                slug=fake.slug(),
                name=fake.word(),
                description=fake.text(),
                brand=random.choice(brands),
                category=random.choice(categories),
                is_active=True,
            )
            products.append(product)

        # Create Product Inventory
        for product in products:
            ProductInventory.objects.create(
                sku=fake.unique.ean(length=13),
                upc=fake.unique.ean(length=12),
                product=product,
                stock=random.randint(0, 100),
                is_active=True,
                retail_price=random.uniform(50, 500),
                store_price=random.uniform(30, 450),
                sale_price=random.uniform(20, 400),
                weight=random.uniform(1, 10),
            )
