import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


# ---------------------------------
# Common Fixtures
# ---------------------------------
@pytest.fixture
def api_client():
    """Provides an instance of APIClient."""
    return APIClient()


@pytest.fixture
def user(db):
    """Provides a regular user."""
    return User.objects.create_user(
        email="user@example.com",
        username="username1",
        password="testpassword",
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    """Provides an admin user."""
    return User.objects.create_superuser(
        email="admin@example.com",
        username="admin",
        password="adminpassword",
        is_active=True,
    )


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """Provides an authenticated client with admin user."""
    token = AccessToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")
    return api_client


@pytest.fixture
def authenticated_user_client(api_client, user):
    """Provides an authenticated client with regular user."""
    api_client.force_authenticate(user=user)
    return api_client


# ---------------------------------
# Categories Fixtures
# ---------------------------------
@pytest.fixture
def category_active(db):
    from categories.models import Category

    return Category.objects.create(
        name="Active Category", slug="active-category", is_active=True
    )


@pytest.fixture
def category_inactive(db):
    from categories.models import Category

    return Category.objects.create(
        name="Inactive Category", slug="inactive-category", is_active=False
    )


# ---------------------------------
# Test Settings Overrides
# ---------------------------------
@pytest.fixture(autouse=True)
def configure_rest_framework_settings(settings):
    """Overrides REST framework settings for testing."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_CLASSES": [],
        "DEFAULT_THROTTLE_RATES": {},
    }
