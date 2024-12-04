from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import (
    User,  # به‌روزرسانی مسیر واردات مدل کاربر بر اساس پروژه شما
)


class LogoutViewTest(TestCase):
    def setUp(self):
        # ایجاد کاربر برای تست
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # ایجاد توکن معتبر برای تست
        self.refresh_token = RefreshToken.for_user(self.user)

        # مسیر درخواست برای لاگ‌اوت
        self.logout_url = "/api/logout/"

    def test_successful_logout(self):
        """تست درخواست POST با توکن معتبر"""
        response = self.client.post(
            self.logout_url, {"refresh": str(self.refresh_token)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logged out successfully.")

    def test_invalid_token_logout(self):
        """تست درخواست POST با توکن نامعتبر"""
        response = self.client.post(self.logout_url, {"refresh": "invalidtoken123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token.")

    def test_missing_token_logout(self):
        """تست درخواست POST بدون ارسال توکن"""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("error" in response.data)

    def test_logout_server_error(self):
        """تست درخواست POST که منجر به خطای سرور می‌شود"""
        # شبیه‌سازی خطای سرور با درخواست POST بدون توکن
        with self.assertRaises(Exception):
            response = self.client.post(self.logout_url, {"refresh": "somevalidtoken"})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["error"], "An error occurred during logout.")
