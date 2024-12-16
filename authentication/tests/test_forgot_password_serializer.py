import pytest
from django.contrib.auth import get_user_model

from authentication.serializers import ForgotPasswordSerializer

User = get_user_model()


@pytest.mark.django_db
class TestForgotPasswordSerializer:
    """Test suite for ForgotPasswordSerializer."""

    @pytest.fixture(autouse=True)
    def setup_user(self):
        """Set up test data."""
        User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password@123",
        )

    def test_valid_email(self):
        """Test that a valid email returns the email as is."""
        data = {"email": "testuser@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        assert serializer.is_valid() is True
        assert serializer.validated_data["email"] == "testuser@example.com"

    def test_email_not_registered(self):
        """Test that an unregistered email returns a validation error."""
        data = {"email": "nonexistent@example.com"}
        serializer = ForgotPasswordSerializer(data=data)

        is_valid = serializer.is_valid(raise_exception=False)

        assert is_valid is False
        assert "email" in serializer.errors
        assert serializer.errors["email"][0] == "This email is not registered."

    def test_invalid_email_format(self):
        """Test that an invalid email format returns a validation error."""
        data = {"email": "invalidemail.com"}
        serializer = ForgotPasswordSerializer(data=data)
        assert serializer.is_valid() is False
        assert "email" in serializer.errors

    def test_blank_email(self):
        """Test that a blank email returns a validation error."""
        data = {"email": ""}
        serializer = ForgotPasswordSerializer(data=data)
        assert serializer.is_valid() is False
        assert "email" in serializer.errors
