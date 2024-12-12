from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from authentication.utils_otp_and_tokens import store_otp_for_user


@pytest.fixture
def api_client():
    """Fixture to provide a DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, db):
    """Fixture to create an authenticated user and return an API client."""
    user = User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="password123",
        is_2fa_enabled=False,
        two_fa_method=None,
    )
    api_client.force_authenticate(user)
    return api_client, user


def test_enable_2fa_success(authenticated_client):
    """Test enabling 2FA successfully."""
    client, user = authenticated_client
    url = reverse("enable_2fa")
    data = {"method": "email"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "2FA has been enabled using email."

    user.refresh_from_db()
    assert user.is_2fa_enabled is True
    assert user.two_fa_method == "email"


def test_enable_2fa_already_enabled(authenticated_client):
    """Test enabling 2FA when it is already enabled."""
    client, user = authenticated_client
    user.is_2fa_enabled = True
    user.two_fa_method = "email"
    user.save()

    url = reverse("enable_2fa")
    data = {"method": "sms"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "2FA is already enabled."


def test_generate_otp_success(authenticated_client):
    """Test generating OTP successfully."""
    client, user = authenticated_client
    user.is_2fa_enabled = True
    user.two_fa_method = "email"
    user.save()

    url = reverse("generate_otp")
    data = {"method": "email"}

    with patch("authentication.tasks.send_otp_via_email.delay") as mock_send_email:
        response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "OTP sent via email."

    mock_send_email.assert_called_once()


def test_generate_otp_2fa_not_enabled(authenticated_client):
    """Test generating OTP when 2FA is not enabled."""
    client, user = authenticated_client

    url = reverse("generate_otp")
    data = {"method": "email"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "2FA is not enabled or method mismatch."


def test_verify_otp_success(authenticated_client):
    """Test verifying OTP successfully."""
    client, user = authenticated_client
    store_otp_for_user(user.id, "123456", ttl=300)

    url = reverse("verify_otp")
    data = {"otp": "123456"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "OTP verified successfully."


def test_verify_otp_invalid(authenticated_client):
    """Test verifying OTP with an invalid code."""
    client, user = authenticated_client
    store_otp_for_user(user.id, "123456", ttl=300)

    url = reverse("verify_otp")
    data = {"otp": "654321"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid or expired OTP."


def test_disable_2fa_success(authenticated_client):
    """Test disabling 2FA successfully."""
    client, user = authenticated_client
    user.is_2fa_enabled = True
    user.set_password("password123")
    user.save()

    url = reverse("disable_2fa")
    data = {"password": "password123"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "2FA has been disabled successfully."

    user.refresh_from_db()
    assert user.is_2fa_enabled is False
    assert user.two_fa_method is None


def test_disable_2fa_invalid_password(authenticated_client):
    """Test disabling 2FA with an invalid password."""
    client, user = authenticated_client
    user.is_2fa_enabled = True
    user.set_password("password123")
    user.save()

    url = reverse("disable_2fa")
    data = {"password": "wrongpassword"}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Invalid password."
