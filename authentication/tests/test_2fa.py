from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils.timezone import now

from authentication.models import User


@pytest.fixture
def create_user(db):
    """Fixture to create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
        phone_number="1234567890",  # Add phone number
    )


@pytest.fixture
def api_client():
    """Fixture to provide API client."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.mark.django_db
class Test2FA:
    @pytest.fixture(autouse=True)
    def setup(self, create_user):
        self.user = create_user

    def authenticate(self, client):
        """Helper method to authenticate the test user."""
        response = client.post(
            reverse("token_obtain_pair"),
            {"username": self.user.username, "password": "testpassword"},
        )
        assert response.status_code == 200
        token = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    @patch("authentication.tasks.send_otp_via_email.delay")
    def test_generate_otp_success_email(self, mock_send_email, api_client):
        """Test successful generation of OTP with email."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        self.authenticate(api_client)
        url = reverse("generate_otp")
        data = {"method": "email"}
        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data["message"] == "OTP sent via email."
        self.user.refresh_from_db()
        assert self.user.otp_code is not None
        assert self.user.otp_expiry > now()
        mock_send_email.assert_called_once_with(
            "Your OTP Code",
            f"Your OTP code is: {self.user.otp_code}. It will expire in 5 minutes.",
            "no-reply@example.com",
            [self.user.email],
        )

    @patch("authentication.tasks.send_otp_via_sms.delay")
    def test_generate_otp_success_sms(self, mock_send_sms, api_client):
        """Test successful generation of OTP with SMS."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "sms"
        self.user.phone_number = "1234567890"  # Add a phone number field to User model
        self.user.save()

        self.authenticate(api_client)
        url = reverse("generate_otp")
        data = {"method": "sms"}
        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data["message"] == "OTP sent via sms."
        self.user.refresh_from_db()
        assert self.user.otp_code is not None
        assert self.user.otp_expiry > now()
        mock_send_sms.assert_called_once_with(
            self.user.phone_number, self.user.otp_code
        )
