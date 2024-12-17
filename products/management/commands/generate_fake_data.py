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
