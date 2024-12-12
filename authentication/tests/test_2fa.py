from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class TwoFactorAuthTests(APITestCase):
    def setUp(self):
        self.user_password = "StrongPassword123!"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.user_password,
            is_2fa_enabled=False,
            two_fa_method=None,
        )
        self.client = APIClient()

        # URL endpoints
        self.enable_2fa_url = reverse("enable_2fa")
        self.generate_otp_url = reverse("generate_otp")
        self.verify_otp_url = reverse("verify_otp")
        self.disable_2fa_url = reverse("disable_2fa")

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    # -------------------- Tests for Enable2FAView --------------------
    def test_enable_2fa_success_email(self):
        self.authenticate()
        data = {"method": "email"}
        response = self.client.post(self.enable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_2fa_enabled)
        self.assertEqual(self.user.two_fa_method, "email")

    def test_enable_2fa_success_sms(self):
        self.authenticate()
        self.user.phone_number = "+11234567890"
        self.user.save()
        data = {"method": "sms"}
        response = self.client.post(self.enable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_2fa_enabled)
        self.assertEqual(self.user.two_fa_method, "sms")

    def test_enable_2fa_already_enabled(self):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        data = {"method": "sms"}
        response = self.client.post(self.enable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enable_2fa_unauthenticated(self):
        data = {"method": "email"}
        client = APIClient()
        response = client.post(self.enable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------- Tests for GenerateOTPView --------------------
    @patch("authentication.views.store_otp_for_user")
    @patch("authentication.tasks.send_otp_via_email.delay")
    @patch("authentication.tasks.send_otp_via_sms.delay")
    def test_generate_otp_success_email(
        self, mock_send_sms, mock_send_email, mock_store_otp
    ):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        data = {"method": "email"}
        response = self.client.post(self.generate_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_store_otp.assert_called_once()
        mock_send_email.assert_called_once()
        mock_send_sms.assert_not_called()

    @patch("authentication.views.store_otp_for_user")
    @patch("authentication.tasks.send_otp_via_email.delay")
    @patch("authentication.tasks.send_otp_via_sms.delay")
    def test_generate_otp_success_sms(
        self, mock_send_sms, mock_send_email, mock_store_otp
    ):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "sms"
        self.user.phone_number = "+11234567890"
        self.user.save()

        data = {"method": "sms"}
        response = self.client.post(self.generate_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_store_otp.assert_called_once()
        mock_send_sms.assert_called_once()
        mock_send_email.assert_not_called()

    def test_generate_otp_2fa_not_enabled(self):
        self.authenticate()
        data = {"method": "email"}
        response = self.client.post(self.generate_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_otp_method_mismatch(self):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        data = {"method": "sms"}
        response = self.client.post(self.generate_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_otp_unauthenticated(self):
        data = {"method": "email"}
        client = APIClient()
        response = client.post(self.generate_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------- Tests for VerifyOTPView --------------------
    @patch("authentication.views.get_otp_for_user")
    @patch("authentication.views.delete_otp_for_user")
    def test_verify_otp_success(self, mock_delete_otp, mock_get_otp):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        mock_get_otp.return_value = "123456"
        data = {"otp": "123456"}
        response = self.client.post(self.verify_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_delete_otp.assert_called_once()

    @patch("authentication.views.get_otp_for_user")
    def test_verify_otp_invalid_or_expired(self, mock_get_otp):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        mock_get_otp.return_value = None
        data = {"otp": "123456"}
        response = self.client.post(self.verify_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("authentication.views.get_otp_for_user")
    def test_verify_otp_incorrect(self, mock_get_otp):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        mock_get_otp.return_value = "123456"
        data = {"otp": "654321"}
        response = self.client.post(self.verify_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_verify_otp_unauthenticated(self):
        data = {"otp": "123456"}
        client = APIClient()
        response = client.post(self.verify_otp_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------- Tests for Disable2FAView --------------------
    def test_disable_2fa_success(self):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.set_password(self.user_password)
        self.user.save()

        data = {"password": self.user_password}
        response = self.client.post(self.disable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_2fa_enabled)
        self.assertIsNone(self.user.two_fa_method)

    def test_disable_2fa_not_enabled(self):
        self.authenticate()
        self.user.is_2fa_enabled = False
        self.user.save()

        data = {"password": self.user_password}
        response = self.client.post(self.disable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disable_2fa_invalid_password(self):
        self.authenticate()
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.set_password(self.user_password)
        self.user.save()

        data = {"password": "WrongPass"}
        response = self.client.post(self.disable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_2fa_enabled)

    def test_disable_2fa_unauthenticated(self):
        data = {"password": self.user_password}
        client = APIClient()
        response = client.post(self.disable_2fa_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
