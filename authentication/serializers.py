from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class EmptySerializer(serializers.Serializer):
    pass


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

        # Custom validation to ensure password doesn't contain HTML tags
        if "<" in password1 or ">" in password1:
            raise serializers.ValidationError(
                {"password": "Password must not contain HTML tags."}
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
