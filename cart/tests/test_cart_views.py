from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from cart.models import Cart, CartItem, CartStatus
from cart.services import CartService
from categories.models import Category
from products.models import Product

User = get_user_model()


@pytest.mark.django_db
class TestCartEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="testpassword",
        )
        self.admin_user = User.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="adminpassword",
        )

        # Generate JWT tokens
        user_access = AccessToken.for_user(self.user)
        admin_access = AccessToken.for_user(self.admin_user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_access}")

        # Clear Redis cart
        CartService.clear_cart(self.user.id)

        # Create sample brand, category, and products
        self.brand = Brand.objects.create(name="Test Brand", slug="test-brand")
        self.category = Category.objects.create(
            name="Test Category", slug="test-category"
        )

        self.product1 = Product.objects.create(
            web_id="unique-1",
            slug="test-product",
            name="Test Product",
            description="Description 1",
            brand=self.brand,
            category=self.category,
        )
        self.product2 = Product.objects.create(
            web_id="unique-2",
            slug="test-product-2",
            name="Test Product 2",
            description="Description 2",
            brand=self.brand,
            category=self.category,
        )

    # --------------------
    # User Endpoints
    # --------------------

    def test_cart_list_empty(self):
        url = reverse("cart-list")
        response = self.client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_amount"] == "0"

    def test_cart_add_item(self):
        url = reverse("cart-add-item")
        response = self.client.post(
            url, {"product_id": self.product1.id, "quantity": 2}, format="json"
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Item added to cart"

        cart_data = CartService.get_all_items(self.user.id)
        assert cart_data[str(self.product1.id)] == "2"

    def test_cart_remove_item(self):
        CartService.add_item(self.user.id, self.product1.id, 3)

        url = reverse("cart-remove-item")
        response = self.client.post(
            url, {"product_id": self.product1.id}, format="json"
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Item removed from cart"

        cart_data = CartService.get_all_items(self.user.id)
        assert str(self.product1.id) not in cart_data

    def test_cart_update_item_quantity(self):
        CartService.add_item(self.user.id, self.product1.id, 2)

        url = reverse("cart-update-item")
        response = self.client.post(
            url, {"product_id": self.product1.id, "quantity": 5}, format="json"
        )
        assert response.status_code == 200
        assert response.json()["detail"] == "Item quantity updated"

        cart_data = CartService.get_all_items(self.user.id)
        assert cart_data[str(self.product1.id)] == "5"

    def test_cart_checkout(self):
        CartService.add_item(self.user.id, self.product1.id, 2)

        url = reverse("cart-checkout")
        response = self.client.post(url, {}, format="json")
        assert response.status_code == 200

        cart = Cart.objects.get(user=self.user)
        assert cart.status == CartStatus.COMPLETED
        assert cart.total_amount == Decimal("0.00")

    def test_cart_checkout_empty(self):
        url = reverse("cart-checkout")
        response = self.client.post(url, {}, format="json")
        assert response.status_code == 400
        assert response.json()["detail"] == "Cart is empty"

    def test_cart_unauthenticated_access(self):
        client = APIClient()
        url = reverse("cart-list")
        response = client.get(url)
        assert response.status_code == 401

    # --------------------
    # Admin Endpoints
    # --------------------

    def test_admin_cart_list(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin_user)}"
        )

        cart = Cart.objects.create(user=self.user, total_amount=Decimal("30.00"))
        CartItem.objects.create(
            cart=cart, product=self.product1, quantity=3, price=Decimal("10.00")
        )

        url = reverse("admin-cart-list")
        response = self.client.get(url)
        assert response.status_code == 200

        data = response.json()
        assert data["count"] == 1  # Check the count of carts
        assert len(data["results"]) == 1  # Check the number of results
        assert data["results"][0]["id"] == cart.id
        assert data["results"][0]["status"] == "active"

    def test_admin_cart_detail(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(self.admin_user)}"
        )

        cart = Cart.objects.create(user=self.user, total_amount=Decimal("30.00"))
        CartItem.objects.create(
            cart=cart, product=self.product1, quantity=3, price=Decimal("10.00")
        )

        url = reverse("admin-cart-detail", args=[cart.id])
        response = self.client.get(url)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == cart.id
        assert data["total_amount"] == "30.00"
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 3
