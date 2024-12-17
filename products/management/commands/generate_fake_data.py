import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from brands.models import Brand
from categories.models import Category
from products.models import Media, Product, ProductInventory, ProductType
from reviews.models import ProductReview

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Generate fake data for the e-commerce project"

    def handle(self, *args, **options):
        self.stdout.write("Generating fake data...")

        # Create Users
        users = [
            User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password="password123",
                is_active=True,
            )
            for _ in range(20)
        ]

        # Create Brands
        brands = [
            Brand.objects.create(
                name=fake.company(),
                slug=fake.slug(),
                description=fake.text(),
                logo=fake.image_url(),
            )
            for _ in range(10)
        ]

        # Create Categories
        categories = [
            Category.objects.create(
                name=fake.word(),
                slug=fake.slug(),
                is_active=True,
            )
            for _ in range(5)
        ]

        # Create Product Types
        product_types = [
            ProductType.objects.create(
                name=fake.word(),
                slug=fake.slug(),
            )
            for _ in range(5)
        ]

        # Create Products
        products = [
            Product.objects.create(
                web_id=fake.unique.uuid4(),
                slug=fake.slug(),
                name=fake.word(),
                description=fake.text(),
                brand=random.choice(brands),
                category=random.choice(categories),
                is_active=True,
            )
            for _ in range(50)
        ]

        # Create Product Inventory
        for product in products:
            ProductInventory.objects.create(
                sku=fake.unique.ean(length=13),
                upc=f"{fake.unique.random_number(digits=12)}",
                product=product,
                product_type=random.choice(
                    product_types
                ),  # Ensure product_type is assigned
                stock=random.randint(0, 100),
                is_active=True,
                retail_price=random.uniform(50, 500),
                store_price=random.uniform(30, 450),
                sale_price=random.uniform(20, 400),
                weight=random.uniform(1, 10),
            )

        # Create Media
        for product in products:
            Media.objects.create(
                product=product,
                image=fake.image_url(),
                is_feature=random.choice([True, False]),
                ordering=random.randint(1, 10),
            )

        # Create Product Reviews
        for product in products:
            for _ in range(random.randint(1, 5)):
                ProductReview.objects.create(
                    user=random.choice(users),
                    product=product,
                    title=fake.sentence(),
                    review=fake.paragraph(),
                    rating=random.randint(1, 5),
                    date=fake.date_time_this_year(),
                    is_approved=True,
                )

        self.stdout.write(self.style.SUCCESS("Fake data generated successfully!"))