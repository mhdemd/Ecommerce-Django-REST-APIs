import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestChangePasswordView:
    """Group all tests for the Change Password View."""

    @pytest.fixture(autouse=True)
    def setup_user_and_url(self, api_client):
        """Set up user and authenticate client for password change tests."""
        self.user = User.objects.create_user(
            username="testuser", password="oldpassword123", email="test@example.com"
        )
        api_client.force_authenticate(user=self.user)
        self.client = api_client
        self.change_password_url = "/auth/api/change-password/"

    def test_successful_password_change(self):
        """Test changing password with valid old and new passwords"""
        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123",
            "new_password2": "newpassword123",
        }
        response = self.client.post(self.change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Password changed successfully."

        # Verify the new password works
        self.user.refresh_from_db()
        assert self.user.check_password("newpassword123")

    def test_incorrect_old_password(self):
        """Test changing password with an incorrect old password"""
        data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123",
            "new_password2": "newpassword123",
        }
        response = self.client.post(self.change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Old password is incorrect."

    def test_invalid_new_password(self):
        """Test changing password with a new password that does not meet validation criteria"""
        data = {
            "old_password": "oldpassword123",
            "new_password": "short",
            "new_password2": "short",
        }
        response = self.client.post(self.change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert (
            "This password is too short. It must contain at least 9 characters."
            in response.data["non_field_errors"]
        )

    def test_missing_old_password(self):
        """Test changing password with missing old password"""
        data = {"new_password": "newpassword123", "new_password2": "newpassword123"}
        response = self.client.post(self.change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_missing_new_password(self):
        """Test changing password with missing new password"""
        data = {"old_password": "oldpassword123"}
        response = self.client.post(self.change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data

    def test_unauthenticated_user(self, api_client):
        """Test accessing the password change endpoint without authentication"""
        api_client.force_authenticate(user=None)

        data = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123",
            "new_password2": "newpassword123",
        }
        response = api_client.post(self.change_password_url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.data
