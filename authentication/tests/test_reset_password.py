import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.test import APIClient

from authentication.utils_otp_and_tokens import store_password_reset_token

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_with_token():
    """
    Creates a user with a valid verification token.
    """
    user = User.objects.create_user(
        username="testuser", email="testuser@example.com", password="old_password123"
    )
    user.verification_token = "valid_token"
    user.token_expiration = now() + timedelta(hours=1)  # Token valid for 1 hour
    user.save()
    return user


@pytest.fixture
def expired_user_with_token():
    """
    Creates a user with an expired verification token.
    """
    user = User.objects.create_user(
        username="testuser", email="expireduser@example.com", password="old_password123"
    )
    user.verification_token = "expired_token"
    user.token_expiration = now() - timedelta(hours=1)  # Token expired 1 hour ago
    user.save()
    return user


@pytest.mark.django_db
def test_reset_password_success(api_client, user_with_token):
    """Test successful password reset."""
    url = reverse("reset_password")
    token = "valid_token"
    store_password_reset_token(token, user_with_token.id, ttl=3600)

    data = {
        "new_password": "new_password123",
        "new_password2": "new_password123",
    }
    response = api_client.post(url + f"?token={token}", data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Password reset successful."


@pytest.mark.django_db
def test_reset_password_missing_token(api_client):
    url = reverse("reset_password")
    data = {
        "new_password": "new_password123",
        "new_password2": "new_password123",
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Token is required in query parameters."


@pytest.mark.django_db
def test_reset_password_expired_token(api_client, expired_user_with_token):
    url = reverse("reset_password")
    data = {
        "new_password": "new_password123",
        "new_password2": "new_password123",
    }
    response = api_client.post(
        url + f"?token={expired_user_with_token.verification_token}", data
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Token is invalid or expired."


@pytest.mark.django_db
def test_reset_password_user_not_found(api_client):
    """Test handling a user not found for a given token."""
    url = reverse("reset_password")
    data = {"new_password": "new_password123", "new_password2": "new_password123"}
    response = api_client.post(url + "?token=invalid_token", data)
    print(response.data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Token is invalid or expired."


@pytest.mark.django_db
def test_reset_password_mismatched_passwords(api_client, user_with_token):
    """Test handling mismatched passwords during reset."""
    url = reverse("reset_password")
    token = "valid_token"
    store_password_reset_token(token, user_with_token.id, ttl=3600)

    data = {
        "new_password": "new_password123",
        "new_password2": "different_password",
    }
    response = api_client.post(url + f"?token={token}", data)
    print(response.data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password" in response.data  # Ensure 'new_password' key exists
    assert response.data["new_password"][0] == "Passwords do not match."
