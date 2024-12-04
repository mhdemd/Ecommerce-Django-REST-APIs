from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LogoutViewTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a valid token for testing
        self.refresh_token = RefreshToken.for_user(self.user)

        # Request path for logout
        self.logout_url = f"{settings.SITE_URL}/auth/api/logout/"

    def test_successful_logout(self):
        """Test POST request with valid token"""
        response = self.client.post(
            self.logout_url, {"refresh": str(self.refresh_token)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Logged out successfully.")

    def test_invalid_token_logout(self):
        """Test POST request with invalid token"""
        response = self.client.post(
            self.logout_url, {"refresh": str(self.refresh_token) + "invalid token"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid token.")

    def test_missing_token_logout(self):
        """Test POST request without sending token"""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue("error" in response.data)

    def test_logout_server_error(self):
        """POST request test that results in a server error"""
        # Simulate a server error with a POST request without a token
        with self.assertRaises(Exception):
            response = self.client.post(self.logout_url, {"refresh": "somevalidtoken"})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.data["error"], "An error occurred during logout.")
