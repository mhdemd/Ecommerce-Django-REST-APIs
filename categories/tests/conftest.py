import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from categories.models import Category

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="user@example.com",
        username="username1",
        password="testpassword",
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        email="admin@example.com",
        username="admin",
        password="adminpassword",
        is_active=True,
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_api_client(admin_user, api_client):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category_active(db):
    return Category.objects.create(
        name="Active Category", slug="active-category", is_active=True
    )


@pytest.fixture
def category_inactive(db):
    return Category.objects.create(
        name="Inactive Category", slug="inactive-category", is_active=False
    )
