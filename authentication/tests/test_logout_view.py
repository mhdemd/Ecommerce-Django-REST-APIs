import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.mark.django_db
class TestLogoutView:
    """Test suite for Logout API endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self, api_client, db):
        """Setup user, client, and valid token."""
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )
        self.client = api_client
        self.client.force_authenticate(user=self.user)

        # Create a valid token for testing
        self.refresh_token = RefreshToken.for_user(self.user)

        # Request path for logout
        self.logout_url = f"{settings.SITE_URL}/auth/api/logout/"

    def test_successful_logout(self):
        """Test POST request with valid token."""
        response = self.client.post(
            self.logout_url, {"refresh": str(self.refresh_token)}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Logged out successfully."

    def test_invalid_token_logout(self):
        """Test POST request with invalid token."""
        response = self.client.post(
            self.logout_url, {"refresh": str(self.refresh_token) + "invalid token"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Invalid token."

    def test_missing_token_logout(self):
        """Test POST request without sending token."""
        response = self.client.post(self.logout_url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_logout_server_error(self, mocker):
        """POST request test that results in a server error."""
        # Simulate a server error by mocking the logout view
        mocker.patch(
            "authentication.views.LogoutView.post",
            side_effect=Exception("An error occurred during logout"),
        )

        with pytest.raises(Exception, match="An error occurred during logout"):
            self.client.post(self.logout_url, {"refresh": "somevalidtoken"})
