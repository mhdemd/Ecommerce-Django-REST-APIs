from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class VerifyEmailViewTest(APITestCase):

    def setUp(self):
        # ایجاد یک کاربر با توکن معتبر برای تست
        self.user = User.objects.create(
            username="testuser",
            email="test@example.com",
            verification_token="validtoken123",
            token_expiration=timezone.now() + timezone.timedelta(hours=1),
            is_active=False,
        )

    def test_verify_email_success(self):
        response = self.client.get("/path/to/verify-email/", {"token": "validtoken123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Email verified successfully.")
        # بررسی تغییر وضعیت کاربر
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.verification_token)

    def test_verify_email_token_expired(self):
        # تنظیم زمان انقضا به یک زمان گذشته
        self.user.token_expiration = timezone.now() - timezone.timedelta(hours=1)
        self.user.save()

        response = self.client.get("/path/to/verify-email/", {"token": "validtoken123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token has expired.")

    def test_verify_email_invalid_token(self):
        response = self.client.get("/path/to/verify-email/", {"token": "invalidtoken"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token.")

    def test_verify_email_missing_token(self):
        response = self.client.get("/path/to/verify-email/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token is required.")
