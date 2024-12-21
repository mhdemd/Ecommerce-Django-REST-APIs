import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from brands.models import Brand
from cart.models import Cart, CartItem, CartStatus
from categories.models import Category
from products.models import Product

User = get_user_model()


@pytest.mark.django_db
def test_cart_model_creation():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass"
    )
    cart = Cart.objects.create(user=user)
    assert cart.id is not None
    assert cart.status == CartStatus.ACTIVE
    assert cart.total_amount == 0


@pytest.mark.django_db
def test_cart_item_model_creation():
    user = User.objects.create_user(
        username="testuser2", email="test2@example.com", password="testpass"
    )
    brand = Brand.objects.create(name="Test Brand", slug="test-brand", is_active=True)
    category = Category.objects.create(
        name="Test Category", slug="test-cat", is_active=True
    )
    product = Product.objects.create(
        web_id="unique-1",
        slug="test-product",
        name="Test Product",
        description="Some description",
        brand=brand,
        category=category,
    )
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(
        cart=cart, product=product, quantity=2, price=100
    )
    assert cart_item.id is not None
    assert cart_item.cart == cart
    assert cart_item.product == product
    assert cart_item.quantity == 2
    assert cart_item.price == 100


@pytest.mark.django_db
def test_cart_item_unique_together():
    user = User.objects.create_user(
        username="testuser3", email="test3@example.com", password="testpass"
    )
    brand = Brand.objects.create(name="Test Brand2", slug="test-brand2", is_active=True)
    category = Category.objects.create(
        name="Test Category2", slug="test-cat2", is_active=True
    )
    product = Product.objects.create(
        web_id="unique-2",
        slug="another-product",
        name="Another Product",
        description="desc",
        brand=brand,
        category=category,
    )
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1, price=50)
    with pytest.raises(IntegrityError):
        # Should raise because cart+product must be unique
        CartItem.objects.create(cart=cart, product=product, quantity=1, price=50)
