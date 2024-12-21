import pytest
from django.contrib.auth import get_user_model

from cart.models import Cart, CartItem, CartStatus
from products.models import Product

User = get_user_model()


@pytest.mark.django_db
def test_cart_model_creation():
    user = User.objects.create_user(email="test@example.com", password="testpass")
    cart = Cart.objects.create(user=user)
    assert cart.id is not None
    assert cart.status == CartStatus.ACTIVE
    assert cart.total_amount == 0


@pytest.mark.django_db
def test_cart_item_model_creation():
    user = User.objects.create_user(email="test2@example.com", password="testpass")
    product = Product.objects.create(name="Test Product", price=99.99)
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(
        cart=cart, product=product, quantity=2, price=product.price
    )
    assert cart_item.id is not None
    assert cart_item.cart == cart
    assert cart_item.product == product
    assert cart_item.quantity == 2
    assert cart_item.price == product.price
