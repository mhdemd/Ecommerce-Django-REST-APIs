import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from brands.models import Brand
from categories.models import Category
from products.models import Product

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


@pytest.fixture
def admin_api_client(admin_user, api_client):
    """Provides an API client authenticated as admin using force_authenticate."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def verify_email_setup(db):
    """Setup user and URL for verify email tests."""
    user = User.objects.create(
        username="testuser",
        email="test@example.com",
        is_active=False,
    )
    verify_email_url = reverse("verify_email")
    return user, verify_email_url


# ---------------------------------
# Brand Fixtures
# ---------------------------------
@pytest.fixture
def brand(db):
    """Create a brand for products."""
    return Brand.objects.create(name="Test Brand", slug="test-brand")


# ---------------------------------
# Product Fixtures
# ---------------------------------
@pytest.fixture
def product(db, brand, category_active):
    """Create a product for testing."""
    return Product.objects.create(
        web_id="12345",
        slug="test-product",
        name="Test Product",
        description="A test product",
        brand=brand,
        category=category_active,
        is_active=True,
    )


# ---------------------------------
# Categories Fixtures
# ---------------------------------
@pytest.fixture
def category_active(db):
    """Creates an active category."""
    return Category.objects.create(
        name="Active Category", slug="active-category", is_active=True
    )


@pytest.fixture
def category_inactive(db):
    """Creates an inactive category."""
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
