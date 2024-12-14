import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from categories.models import Category

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="user@example.com", password="testpassword", is_active=True
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpassword", is_active=True
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_api_client(admin_user, api_client):
    api_client.force_authenticate(user=admin_user)
    return api_client
