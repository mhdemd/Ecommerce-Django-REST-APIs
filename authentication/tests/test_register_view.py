from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase

from ..serializers import RegisterSerializer


class RegisterSerializerTest(APITestCase):
    def test_passwords_match(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password@P",
            "password2": "password@P",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_passwords_do_not_match(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "password2": "differentpassword",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {"password"})

    def test_password_without_html_tags(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "<script>alert('hack');</script>",
            "password2": "<script>alert('hack');</script>",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(set(serializer.errors.keys()), {"password"})

    def test_password_too_short(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short",
            "password2": "short",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        # print(serializer.errors)
        self.assertTrue(
            "This password is too short"
            in str(serializer.errors.get("non_field_errors", ""))
        )

    def test_common_password(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456789",
            "password2": "123456789",
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())

        # print(serializer.errors)
        self.assertTrue(
            "This password is too common"
            in str(serializer.errors.get("non_field_errors", ""))
        )

    def test_password_with_special_characters(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Complex@Password123!",
            "password2": "Complex@Password123!",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_validators(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password123!",
        }
        serializer = RegisterSerializer(data=data)
        try:
            validate_password(data["password"])
            self.assertTrue(serializer.is_valid())
        except ValidationError as e:
            self.fail(f"Password validation failed: {e}")

    def test_user_creation(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password123!",
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
