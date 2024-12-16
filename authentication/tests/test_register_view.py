import pytest
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from authentication.serializers import RegisterSerializer


@pytest.mark.django_db
class TestRegisterSerializer:
    """Test suite for the RegisterSerializer."""

    def test_passwords_match(self):
        """Test that matching passwords are valid."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password@P",
            "password2": "password@P",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is True

    def test_passwords_do_not_match(self):
        """Test that mismatching passwords are invalid."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "differentpassword",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors

    def test_password_without_html_tags(self):
        """Test that passwords with HTML tags are invalid."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "<script>alert('hack');</script>",
            "password2": "<script>alert('hack');</script>",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "password" in serializer.errors

    def test_password_too_short(self):
        """Test that too-short passwords are invalid."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",
            "password2": "short",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "This password is too short" in str(
            serializer.errors.get("non_field_errors", "")
        )

    def test_common_password(self):
        """Test that common passwords are invalid."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456789",
            "password2": "123456789",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is False
        assert "This password is too common" in str(
            serializer.errors.get("non_field_errors", "")
        )

    def test_password_with_special_characters(self):
        """Test that complex passwords with special characters are valid."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Complex@Password123!",
            "password2": "Complex@Password123!",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is True

    def test_password_validators(self):
        """Test that valid passwords pass validation."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password123!",
        }
        serializer = RegisterSerializer(data=data)
        try:
            validate_password(data["password"])
            assert serializer.is_valid() is True
        except ValidationError as e:
            pytest.fail(f"Password validation failed: {e}")

    def test_user_creation(self):
        """Test that a user is created successfully."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password123!",
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid() is True
        user = serializer.save()
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
