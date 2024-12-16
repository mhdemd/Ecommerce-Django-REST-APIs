import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        username="admin", password="adminpass", email="admin@example.com"
    )
    return user


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    api_client.force_login(admin_user)
    return api_client
