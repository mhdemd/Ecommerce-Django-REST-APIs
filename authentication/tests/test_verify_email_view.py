import pytest
from rest_framework import status

from authentication.utils_otp_and_tokens import store_verification_token


@pytest.mark.django_db
class TestVerifyEmailView:
    """Group all tests for the Verify Email View."""

    def test_verify_email_success(self, api_client, verify_email_setup):
        """Test verifying email successfully."""
        user, verify_email_url = verify_email_setup
        token = "valid_token"

        store_verification_token(
            token, user.id, ttl=3600
        )  # Store a valid token in Redis

        response = api_client.get(f"{verify_email_url}?token={token}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Email verified successfully."

        # Check user status change
        user.refresh_from_db()
        assert user.is_active

    def test_verify_email_invalid_token(self, api_client, verify_email_setup):
        """Test verifying email with an invalid token."""
        _, verify_email_url = verify_email_setup

        response = api_client.get(f"{verify_email_url}?token=invalid_token")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Invalid token."

    def test_verify_email_missing_token(self, api_client, verify_email_setup):
        """Test verifying email without providing a token."""
        _, verify_email_url = verify_email_setup

        response = api_client.get(verify_email_url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Token is required."
