import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass",
    )


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    token = AccessToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
    return api_client


@pytest.fixture
def authenticated_user_client(api_client, django_user_model):
    user = django_user_model.objects.create_user(
        username="user", password="testpassword"
    )
    api_client.force_authenticate(user=user)
    return api_client
