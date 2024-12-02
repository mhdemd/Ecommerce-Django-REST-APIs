import bleach
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework import serializers

User = get_user_model()


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
        validate_password(password1)

        # Custom validation to ensure password doesn't contain HTML tags using bleach
        cleaned_password = bleach.clean(password1, tags=[], attributes=[], strip=True)

        if cleaned_password != password1:
            raise serializers.ValidationError(
                {"password": "Password must not contain HTML tags or scripts."}
            )

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
        validate_password(password1)

        # Custom validation to ensure password doesn't contain HTML tags using bleach
        cleaned_password = bleach.clean(password1, tags=[], attributes=[], strip=True)

        if cleaned_password != password1:
            raise serializers.ValidationError(
                {"password": "Password must not contain HTML tags or scripts."}
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
        validate_password(password1)

        # Custom validation to ensure password doesn't contain HTML tags using bleach
        cleaned_password = bleach.clean(password1, tags=[], attributes=[], strip=True)
        if cleaned_password != password1:
            raise serializers.ValidationError(
                {"new_password": "Password must not contain HTML tags or scripts."}
            )

        return data


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
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
        ]

    def clean_input(self, value):
        # Uses bleach to clean the input by removing any HTML or JavaScript tags
        return bleach.clean(
            value,
            tags=[],
            attributes=[],
        )

    def validate_email(self, value):
        # Checks if the email already exists in the database (excluding the current user)
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        # Cleans the input for the username
        value = self.clean_input(value)
        # Checks if the username already exists in the database (excluding the current user)
        if User.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_first_name(self, value):
        # Cleans the input for the first name
        return self.clean_input(value)

    def validate_last_name(self, value):
        # Cleans the input for the last name
        return self.clean_input(value)
