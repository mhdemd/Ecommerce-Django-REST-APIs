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
