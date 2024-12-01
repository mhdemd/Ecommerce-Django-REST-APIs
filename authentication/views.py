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

from .serializers import EmptySerializer, RegisterSerializer

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
            "# Registers a new user and sends a verification link.\n"
            "\n"
            "- The serializer includes built-in validations to prevent XSS attacks, ensuring no field is vulnerable.\n"
            "\n"
            "- Email and password fields are validated according to Django standards to guarantee proper formatting.\n"
            "\n"
            "- Rate limiting is implemented to prevent excessive requests, with customizable limits for added security.\n"
            "\n"
            "- The user model includes 'verification_token' and 'token_expiration' fields to secure the email verification link.\n"
            "\n"
            "- Once the link is used for verification, the token is cleared to maintain security."
        ),
        request=RegisterSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "User registered successfully. Please verify your email.",
                    }
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "detail": {
                        "type": "string",
                        "example": "Validation error details.",
                    }
                },
            },
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

        # Send the verification email
        subject = "Email Verification"
        message = f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n\n{verification_link}\n\nThank you!"
        from_email = "no-reply@example.com"
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return Response(
            {"message": "User registered successfully. Please verify your email."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = EmptySerializer

    @extend_schema(
        tags=["Auth - Registration"],
        summary="Verify Email",
        description=(
            "# Activates a user account after email verification.\n"
            "\n"
            "- When the user clicks on the link sent to their email, this API is called.\n"
            "\n"
            "- The link contains a temporary token that is valid for one hour.\n"
            "\n"
            "- Without the temporary token, you cannot access this API.\n"
        ),
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
