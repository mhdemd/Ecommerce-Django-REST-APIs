import pytest
from django.contrib.auth import get_user_model

from cart.services import CartService
from products.models import Product

User = get_user_model()


@pytest.mark.django_db
def test_add_item_to_redis(settings):
    user = User.objects.create_user(email="redis_user@example.com", password="testpass")
    # Mock or use actual Redis in test environment
    # For example, using settings.REDIS_INSTANCE directly:
    CartService.clear_cart(user.id)
    initial_data = CartService.get_all_items(user.id)
    assert initial_data == {}

    quantity = CartService.add_item(user.id, product_id=1, quantity=3)
    assert quantity == 3
    items = CartService.get_all_items(user.id)
    assert len(items) == 1
    assert items["1"] == "3"


@pytest.mark.django_db
def test_remove_item_from_redis(settings):
    user = User.objects.create_user(
        email="redis_user2@example.com", password="testpass"
    )
    CartService.clear_cart(user.id)
    CartService.add_item(user.id, product_id=5, quantity=2)
    CartService.remove_item(user.id, product_id=5)
    items = CartService.get_all_items(user.id)
    assert items == {}


@pytest.mark.django_db
def test_set_item_quantity_in_redis(settings):
    user = User.objects.create_user(
        email="redis_user3@example.com", password="testpass"
    )
    CartService.clear_cart(user.id)
    CartService.add_item(user.id, product_id=10, quantity=1)
    CartService.set_item_quantity(user.id, product_id=10, quantity=5)
    items = CartService.get_all_items(user.id)
    assert items["10"] == "5"


@pytest.mark.django_db
def test_clear_cart_in_redis(settings):
    user = User.objects.create_user(
        email="redis_user4@example.com", password="testpass"
    )
    CartService.add_item(user.id, product_id=7, quantity=4)
    CartService.clear_cart(user.id)
    items = CartService.get_all_items(user.id)
    assert items == {}
