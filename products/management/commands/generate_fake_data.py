import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from brands.models import Brand
from categories.models import Category
from products.models import (
    Media,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductInventory,
    ProductType,
)
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

        # Create Product Attributes
        attributes = [
            ProductAttribute.objects.create(name="Color"),
            ProductAttribute.objects.create(name="Size"),
            ProductAttribute.objects.create(name="Material"),
        ]

        # Create Product Attribute Values
        attribute_values = {
            "Color": [
                ProductAttributeValue.objects.create(
                    product_attribute=attributes[0], attribute_value=color
                )
                for color in ["Red", "Blue", "Green", "Black", "White"]
            ],
            "Size": [
                ProductAttributeValue.objects.create(
                    product_attribute=attributes[1], attribute_value=size
                )
                for size in ["S", "M", "L", "XL"]
            ],
            "Material": [
                ProductAttributeValue.objects.create(
                    product_attribute=attributes[2], attribute_value=material
                )
                for material in ["Cotton", "Polyester", "Leather"]
            ],
        }

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
            number_of_inventories = random.randint(
                2, 5
            )  # Between 2 and 5 sub-products for each product
            for _ in range(number_of_inventories):
                inventory = ProductInventory.objects.create(
                    sku=fake.unique.ean(length=13),
                    upc=f"{fake.unique.random_number(digits=12)}",
                    product=product,
                    product_type=random.choice(
                        product_types
                    ),  # Ensure product_type is assigned
                    stock=random.randint(0, 100),
                    is_active=True,
                    retail_price=round(
                        random.uniform(50, 500), 2
                    ),  # Random and rounded prices
                    store_price=round(random.uniform(30, 450), 2),
                    sale_price=round(random.uniform(20, 400), 2),
                    weight=round(random.uniform(1, 10), 2),
                )

                # Assign random attribute values to inventory
                for attribute in attributes:
                    inventory.attribute_values.add(
                        random.choice(attribute_values[attribute.name])
                    )

        # Create Media
        for product in products:
            Media.objects.create(
                product=product,
                image="images/default.png",
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
