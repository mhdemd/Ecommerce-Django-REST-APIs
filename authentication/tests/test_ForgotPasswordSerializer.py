from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from ..serializers import ForgotPasswordSerializer

User = get_user_model()


class ForgotPasswordSerializerTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="testuser", email="testuser@example.com", password="password@123"
        )

    def test_valid_email(self):
        """Test that a valid email returns the email as is."""
        data = {"email": "testuser@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "testuser@example.com")

    def test_email_not_registered(self):
        """Test that an unregistered email returns a validation error."""
        data = {"email": "nonexistent@example.com"}
        serializer = ForgotPasswordSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_email_format(self):
        """Test that an invalid email format returns a validation error."""
        data = {"email": "invalidemail.com"}
        serializer = ForgotPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_blank_email(self):
        """Test that a blank email returns a validation error."""
        data = {"email": ""}
        serializer = ForgotPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)
