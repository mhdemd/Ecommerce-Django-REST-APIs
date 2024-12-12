from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.utils_otp_and_tokens import store_verification_token

User = get_user_model()


class VerifyEmailViewTest(APITestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            is_active=False,
        )
        self.verify_email_url = reverse("verify_email")

    def test_verify_email_success(self):
        """Test verifying email successfully."""
        token = "valid_token"
        store_verification_token(
            token, self.user.id, ttl=3600
        )  # Store a valid token in Redis

        response = self.client.get(f"{self.verify_email_url}?token={token}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email verified successfully.")

        # Check user status change
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_verify_email_invalid_token(self):
        """Test verifying email with an invalid token."""
        response = self.client.get(f"{self.verify_email_url}?token=invalid_token")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token.")

    def test_verify_email_missing_token(self):
        """Test verifying email without providing a token."""
        response = self.client.get(self.verify_email_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token is required.")
