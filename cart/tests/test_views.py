import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from products.models import Product

User = get_user_model()


@pytest.mark.django_db
class TestCartViewSet:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com", password="testpass"
        )
        access = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.product = Product.objects.create(name="Test Product", price=100)
        self.product2 = Product.objects.create(name="Another Product", price=50)

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
