from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class VerifyEmailViewTest(APITestCase):

    def setUp(self):
        # Create a user with a valid token for testing
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            verification_token="validtoken123",
            token_expiration=timezone.now() + timezone.timedelta(hours=1),
            is_active=False,
        )
        self.verify_email_url = settings.SITE_URL + reverse("verify_email")

    def test_verify_email_success(self):
        response = self.client.get(f"{self.verify_email_url}?token=validtoken123")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email verified successfully.")
        # Check user status change
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.verification_token)

    def test_verify_email_token_expired(self):
        # Set the expiration time to a past time
        self.user.token_expiration = timezone.now() - timezone.timedelta(hours=1)
        self.user.save()

        response = self.client.get(f"{self.verify_email_url}?token=validtoken123")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token has expired.")

    def test_verify_email_invalid_token(self):
        response = self.client.get(f"{self.verify_email_url}?token=invalidtoken")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token.")

    def test_verify_email_missing_token(self):
        response = self.client.get(self.verify_email_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token is required.")
