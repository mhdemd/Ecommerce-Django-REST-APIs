from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status

from authentication.models import User


@pytest.fixture
def create_user(db):
    """Fixture to create a user in the database."""

    def _create_user(email, username, is_active=False):
        user = User.objects.create_user(
            email=email,
            username=username,
            password="testpassword123",
            is_active=is_active,
        )
        return user

    return _create_user


@pytest.fixture
def api_client():
    """Fixture to provide API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.mark.django_db
class TestResendEmailView:
    @pytest.fixture(autouse=True)
    def setup(self, create_user):
        self.registered_user = create_user("registered@example.com", "registered_user")
        self.active_user = create_user(
            "active@example.com", "active_user", is_active=True
        )

    def test_resend_verification_email_success(self, api_client):
        """Test successful resend of verification email for inactive user."""
        url = reverse("resend_email")
        data = {"email": "registered@example.com", "email_type": "verification"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Verification email resent successfully."

    def test_resend_verification_email_already_verified(self, api_client):
        """Test resend of verification email for already verified user."""
        url = reverse("resend_email")
        data = {"email": "active@example.com", "email_type": "verification"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "User is already verified."

    def test_resend_reset_password_email_success(self, api_client):
        """Test successful resend of password reset email."""
        url = reverse("resend_email")
        data = {"email": "registered@example.com", "email_type": "reset_password"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password reset email resent successfully."

    def test_resend_email_user_not_found(self, api_client):
        """Test resend email for non-existent user."""
        url = reverse("resend_email")
        data = {"email": "nonexistent@example.com", "email_type": "verification"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"] == "User not found."

    def test_resend_email_invalid_type(self, api_client):
        """Test resend email with invalid email_type."""
        url = reverse("resend_email")
        data = {"email": "registered@example.com", "email_type": "invalid_type"}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email_type" in response.data
        assert response.data["email_type"] == ['"invalid_type" is not a valid choice.']

    def test_resend_email_missing_fields(self, api_client):
        """Test resend email with missing fields."""
        url = reverse("resend_email")
        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert "email_type" in response.data
