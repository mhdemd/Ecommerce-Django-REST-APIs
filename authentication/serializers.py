import bleach
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()

from rest_framework.exceptions import ValidationError


def clean_input(value):
    """
    Clean the input by removing any HTML or JavaScript tags.
    """
    if not value:  # Skip cleaning for None or empty values
        return value
    cleaned_value = bleach.clean(value, tags=[], attributes=[], strip=True)
    if cleaned_value != value:
        raise ValidationError("Input contains invalid HTML or scripts.")
    return cleaned_value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, data):
        password1 = data.get("password")
        password2 = data.get("password2")

        # Check if passwords match
        if password1 != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Validate password against Django's built-in password validators
        try:
            validate_password(password1)
        except ValidationError:
            # Generic error message for password validation failures
            raise serializers.ValidationError(
                {"password": "Password does not meet the required criteria."}
            )

        # Use clean_input to validate the password
        try:
            clean_input(password1)
        except ValidationError:
            # Generic error message for invalid input
            raise serializers.ValidationError({"password": "Invalid password input."})

        return data

    def create(self, validated_data):
        # Remove password2 since it's not needed for user creation
        validated_data.pop("password2")
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.is_active = False  # Deactivate until email is verified
        user.save()
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        required=True, help_text="The refresh token to be blacklisted."
    )


# ---------------------------- Password Management Endpoints ----------------------------
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        password1 = data.get("new_password")
        password2 = data.get("new_password2")

        # Check if passwords match
        if password1 != password2:
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )

        # Validate password against Django's built-in password validators
        try:
            validate_password(password1)
        except ValidationError:
            # Generic error message for password validation failures
            raise serializers.ValidationError(
                {"new_password": "Password does not meet the required criteria."}
            )

        # Use clean_input to validate and clean the password
        try:
            clean_input(password1)
        except ValidationError:
            # Generic error message for invalid input
            raise serializers.ValidationError(
                {"new_password": "Invalid password input."}
            )

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is not registered.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True, required=True, allow_blank=False
    )
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password1 = data.get("new_password")
        password2 = data.get("new_password2")

        # Check if passwords match
        if password1 != password2:
            raise serializers.ValidationError(
                {"new_password": "Passwords do not match."}
            )

        # Validate password against Django's built-in password validators
        try:
            validate_password(password1)
        except ValidationError:
            # Generic error message for password validation failures
            raise serializers.ValidationError(
                {"new_password": "Password does not meet the required criteria."}
            )

        return data


class ResendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    email_type = serializers.ChoiceField(
        choices=["verification", "reset_password"], required=True
    )


# ---------------------------- Profile Management Endpoints ----------------------------
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
        ]


class UpdateProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that username already exists.",
            )
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="This email is already in use."
            )
        ]
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

    def validate_username(self, value):
        """
        Clean the username and ensure it meets the requirements.
        """
        return clean_input(value)

    def validate_email(self, value):
        """
        Validate the email and ensure it is unique.
        """
        return value

    def validate_first_name(self, value):
        """
        Clean the first name and remove unwanted HTML.
        """
        return clean_input(value)

    def validate_last_name(self, value):
        """
        Clean the last name and remove unwanted HTML.
        """
        return clean_input(value)


# ---------------------------- OTP Endpoints ----------------------------
class Enable2FASerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=["email", "sms"],
        required=True,
        help_text="Choose between 'email' or 'sms' for 2FA.",
    )


class GenerateOTPSerializer(serializers.Serializer):
    method = serializers.ChoiceField(
        choices=["email", "sms"],
        required=True,
        help_text="Choose 'email' or 'sms' for receiving the OTP.",
    )


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(
        max_length=6, required=True, help_text="Enter the 6-digit OTP you received."
    )


class Disable2FASerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
