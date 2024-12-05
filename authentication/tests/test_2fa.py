import pytest
from django.urls import reverse
from django.utils.timezone import now, timedelta

from authentication.models import User


@pytest.fixture
def create_user(db):
    """Fixture to create a test user."""
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
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
        client.login(username=self.user.username, password="testpassword")

    def test_enable_2fa_success(self, api_client):
        """Test successful activation of 2FA."""
        self.authenticate(api_client)
        url = reverse("enable_2fa")
        data = {"method": "email"}
        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data["message"] == "2FA has been enabled using email."
        self.user.refresh_from_db()
        assert self.user.is_2fa_enabled is True
        assert self.user.two_fa_method == "email"

    def test_enable_2fa_already_enabled(self, api_client):
        """Test enabling 2FA when already enabled."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        self.authenticate(api_client)
        url = reverse("enable_2fa")
        data = {"method": "email"}
        response = api_client.post(url, data)

        assert response.status_code == 400
        assert response.data["error"] == "2FA is already enabled."

    def test_generate_otp_success(self, api_client):
        """Test successful generation of OTP."""
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

    def test_generate_otp_method_mismatch(self, api_client):
        """Test generating OTP with mismatched method."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.save()

        self.authenticate(api_client)
        url = reverse("generate_otp")
        data = {"method": "sms"}  # Method mismatch
        response = api_client.post(url, data)

        assert response.status_code == 400
        assert response.data["error"] == "2FA is not enabled or method mismatch."

    def test_verify_otp_success(self, api_client):
        """Test successful verification of OTP."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.otp_code = "123456"
        self.user.otp_expiry = now() + timedelta(minutes=5)
        self.user.save()

        self.authenticate(api_client)
        url = reverse("verify_otp")
        data = {"otp": "123456"}
        response = api_client.post(url, data)

        assert response.status_code == 200
        assert response.data["message"] == "OTP verified successfully."
        self.user.refresh_from_db()
        assert self.user.otp_code is None  # OTP cleared
        assert self.user.otp_expiry is None

    def test_verify_otp_invalid_code(self, api_client):
        """Test verification with an invalid OTP code."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.otp_code = "123456"
        self.user.otp_expiry = now() + timedelta(minutes=5)
        self.user.save()

        self.authenticate(api_client)
        url = reverse("verify_otp")
        data = {"otp": "654321"}  # Invalid code
        response = api_client.post(url, data)

        assert response.status_code == 400
        assert response.data["error"] == "Invalid or expired OTP."

    def test_verify_otp_expired_code(self, api_client):
        """Test verification with an expired OTP code."""
        self.user.is_2fa_enabled = True
        self.user.two_fa_method = "email"
        self.user.otp_code = "123456"
        self.user.otp_expiry = now() - timedelta(minutes=1)  # Expired
        self.user.save()

        self.authenticate(api_client)
        url = reverse("verify_otp")
        data = {"otp": "123456"}
        response = api_client.post(url, data)

        assert response.status_code == 400
        assert response.data["error"] == "Invalid or expired OTP."
