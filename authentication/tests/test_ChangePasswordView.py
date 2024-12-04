from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class ChangePasswordViewTest(APITestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username="testuser", password="oldpassword123", email="test@example.com"
        )
        self.client.force_authenticate(user=self.user)
        self.change_password_url = "/auth/api/change-password/"

    def test_successful_password_change(self):
        """Test changing password with valid old and new passwords"""
        data = {"old_password": "oldpassword123", "new_password": "newpassword123"}
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully.")

        # Verify the new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword123"))

    def test_incorrect_old_password(self):
        """Test changing password with an incorrect old password"""
        data = {"old_password": "wrongpassword", "new_password": "newpassword123"}
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Old password is incorrect.")

    def test_invalid_new_password(self):
        """Test changing password with a new password that does not meet validation criteria"""
        data = {"old_password": "oldpassword123", "new_password": "short"}
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.data["error"], "Password does not meet validation criteria."
        )

    def test_missing_old_password(self):
        """Test changing password with missing old password"""
        data = {"new_password": "newpassword123"}
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_missing_new_password(self):
        """Test changing password with missing new password"""
        data = {"old_password": "oldpassword123"}
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", response.data)

    def test_unauthenticated_user(self):
        """Test accessing the password change endpoint without authentication"""
        self.client.logout()  # Ensure the user is logged out
        data = {"old_password": "oldpassword123", "new_password": "newpassword123"}
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
