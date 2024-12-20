import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from cart.services import CartService
from categories.models import Category
from products.models import Product

User = get_user_model()


@pytest.mark.django_db
class TestCartViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_username", email="test@example.com", password="testpass"
        )
        # Clear the user’s cart in Redis
        CartService.clear_cart(self.user.id)

        access = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create brand & category for the product
        self.brand = Brand.objects.create(name="Test Brand", slug="test-brand")
        self.category = Category.objects.create(name="Test Category", slug="test-cat")

        # Now create two Product instances
        self.product = Product.objects.create(
            web_id="unique-1",
            slug="test-product",
            name="Test Product",
            description="Some description",
            brand=self.brand,
            category=self.category,
            # If your Product model has other required fields, add them here
        )

        self.product2 = Product.objects.create(
            web_id="unique-2",
            slug="another-product",
            name="Another Product",
            description="More description",
            brand=self.brand,
            category=self.category,
        )

    def test_list_empty_cart(self):
        list_url = reverse("cart-list")
        response = self.client.get(list_url)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total_amount"] == "0"

    def test_add_item(self):
        url = reverse("cart-add-item")
        response = self.client.post(
            url, {"product_id": self.product.id, "quantity": 2}, format="json"
        )
        assert response.status_code == 200

        list_url = reverse("cart-list")
        response = self.client.get(list_url)
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["items"][0]["product_name"] == self.product.name

    def test_remove_item(self):
        add_url = reverse("cart-add-item")
        self.client.post(
            add_url, {"product_id": self.product.id, "quantity": 2}, format="json"
        )
        remove_url = reverse("cart-remove-item")
        response = self.client.post(remove_url, {"product_id": self.product.id})
        assert response.status_code == 200

        list_url = reverse("cart-list")
        response = self.client.get(list_url)
        data = response.json()
        assert data["items"] == []

    def test_update_item_quantity(self):
        add_url = reverse("cart-add-item")
        self.client.post(
            add_url, {"product_id": self.product.id, "quantity": 2}, format="json"
        )
        update_url = reverse("cart-update-item")
        response = self.client.post(
            update_url, {"product_id": self.product.id, "quantity": 5}, format="json"
        )
        assert response.status_code == 200

        list_url = reverse("cart-list")
        response = self.client.get(list_url)
        data = response.json()
        assert data["items"][0]["quantity"] == 5

    def test_checkout(self):
        add_url = reverse("cart-add-item")
        self.client.post(
            add_url, {"product_id": self.product.id, "quantity": 3}, format="json"
        )
        checkout_url = reverse("cart-checkout")
        response = self.client.post(checkout_url, {})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

        list_url = reverse("cart-list")
        response = self.client.get(list_url)
        data_after = response.json()
        assert len(data_after["items"]) == 0

    def test_checkout_empty_cart(self):
        checkout_url = reverse("cart-checkout")
        response = self.client.post(checkout_url, {})
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Cart is empty"

    def test_unauthorized_access(self):
        client_unauthorized = APIClient()
        list_url = reverse("cart-list")
        response = client_unauthorized.get(list_url)
        assert response.status_code == 401
