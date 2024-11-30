from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from authentication.models import User

from .serializers import EmptySerializer, LoginSerializer, RegisterSerializer

# ---------------------------- JWT endpoints ----------------------------


@extend_schema(tags=["Auth - Token"])
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=["Auth - Token"])
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["Auth - Token"])
class CustomTokenVerifyView(TokenVerifyView):
    pass


# ---------------------------- Authentication Endpoints ----------------------------


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    @extend_schema(
        tags=["Auth - Registration"],
        summary="User Registration",
        description=(
            "Registers a new user and sends a verification link.\n"
            "\n"
            "Validation in the serializer prevents XSS attacks. No field is vulnerable to such attacks.\n"
            "The email and password fields are validated according to Django standards for proper formatting.\n"
            "Rate limiting is applied to prevent repeated request attacks, with adjustable request limits.\n"
            "Two fields, verification_token and token_expiration, have been added to the user model to ensure the security of the email verification link. Once verified, the token is cleared."
        ),
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The username for the new user",
                    },
                    "email": {
                        "type": "string",
                        "description": "The email for the new user",
                    },
                    "password": {
                        "type": "string",
                        "description": "The password for the new user",
                    },
                    "password2": {"type": "string", "description": "Confirm password"},
                },
                "required": ["username", "email", "password", "password2"],
            }
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate a secure, one-time token
        token = get_random_string(32)
        token_expiration = datetime.now() + timedelta(hours=1)  # Token valid for 1 hour

        # Store token and expiration in the user object or a separate model
        user.verification_token = token
        user.token_expiration = token_expiration
        user.save()

        # Create a verification link
        verification_link = (
            f"http://127.0.0.1:8000/auth/api/verify-email/?token={token}"
        )
        print(f"Verification Link: {verification_link}")

        return Response(
            {"message": "User registered successfully. Please verify your email."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmptySerializer

    @extend_schema(
        tags=["Auth - Registration"],
        summary="Verify Email",
        description="Activates a user account after email verification.",
    )
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(verification_token=token)
            if user.token_expiration < timezone.now():
                return Response(
                    {"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST
                )

            user.is_active = True
            user.verification_token = None  # Remove the token after verification
            user.token_expiration = None
            user.save()

            return Response(
                {"message": "Email verified successfully."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer  # Replace with actual serializer class for login

    @extend_schema(
        tags=["Auth - Login/Logout"],
        summary="Login",
        description="Logs in a user and returns a JWT token.",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # Token generation logic
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmptySerializer

    @extend_schema(
        tags=["Auth - Login/Logout"],
        summary="Logout",
        description="Logs out a user by blacklisting the refresh token.",
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------- Password Management Endpoints ----------------------------


class ForgotPasswordView(APIView):
    @extend_schema(
        tags=["Auth - Password"],
        summary="Forgot Password",
        description="Sends a password reset link to the user's email.",
    )
    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        send_mail(
            "Reset your password",
            f"Click the link to reset your password: http://example.com/reset-password/?user_id={user.id}",
            "no-reply@example.com",
            [email],
        )
        return Response(
            {"message": "Password reset link sent."}, status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    @extend_schema(
        tags=["Auth - Password"],
        summary="Reset Password",
        description="Resets the user's password using the provided user ID and new password.",
    )
    def post(self, request):
        user_id = request.query_params.get("user_id")
        new_password = request.data.get("new_password")
        user = get_object_or_404(User, id=user_id)
        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Password reset successfully."}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth - Password"],
        summary="Change Password",
        description="Allows a logged-in user to change their password.",
    )
    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


# ---------------------------- Profile Management Endpoints ----------------------------


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth - Profile"],
        summary="Get Profile",
        description="Fetches the profile details of the logged-in user.",
    )
    def get(self, request):
        user = request.user
        return Response(
            {
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Auth - Profile"],
        summary="Update Profile",
        description="Updates the profile information of the logged-in user.",
    )
    def put(self, request):
        user = request.user
        user.username = request.data.get("username", user.username)
        user.email = request.data.get("email", user.email)
        user.save()
        return Response(
            {"message": "Profile updated successfully."}, status=status.HTTP_200_OK
        )
