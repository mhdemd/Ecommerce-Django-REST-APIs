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
