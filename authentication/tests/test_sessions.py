import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from authentication.models import Session


@pytest.fixture
def api_client():
    """Fixture to provide API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Fixture to create a user for testing."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
    )


@pytest.mark.django_db
def test_list_sessions_success(api_client, create_user):
    """Test successful retrieval of active sessions."""
    user = create_user
    # Add some sessions
    Session.objects.create(user=user, token="token1", device="Chrome")
    Session.objects.create(user=user, token="token2", device="Firefox")

    api_client.force_authenticate(user=user)
    response = api_client.get(reverse("list_sessions"))

    assert response.status_code == 200
    assert len(response.data["sessions"]) == 2


@pytest.mark.django_db
def test_delete_session_success(api_client, create_user):
    """Test successful deletion of a specific session."""
    user = create_user
    session = Session.objects.create(user=user, token="token1", device="Chrome")

    api_client.force_authenticate(user=user)
    response = api_client.post(reverse("delete_session", args=[session.id]))

    assert response.status_code == 200
    assert Session.objects.filter(id=session.id).exists() is False


@pytest.mark.django_db
def test_logout_all_sessions_success(api_client, create_user):
    """Test successful logout from all sessions."""
    user = create_user
    Session.objects.create(user=user, token="token1", device="Chrome")
    Session.objects.create(user=user, token="token2", device="Firefox")

    api_client.force_authenticate(user=user)
    response = api_client.post(reverse("logout_all_sessions"))

    assert response.status_code == 200
    assert Session.objects.filter(user=user).exists() is False
