from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from authentication.models import User

from .serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
)

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
        verification_link = f"{settings.SITE_URL}/auth/api/verify-email/?token={token}"

        # Send the verification email
        subject = "Email Verification"
        message = f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n\n{verification_link}\n\nThank you!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return Response(
            {"message": "User registered successfully. Please verify your email."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(generics.GenericAPIView):

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
        # Get the token directly from query parameters
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
    serializer_class = LogoutSerializer

    @extend_schema(
        tags=["Auth - Logout"],
        summary="Logout",
        description=(
            "# Logs out a user by blacklisting the refresh token.\n"
            "\n"
            "- To use this endpoint, you first need to authorize yourself from the top of the Swagger UI page.\n"
            "\n"
            "- By sending the refresh token, it is added to the blacklist and becomes invalid.\n"
            "\n"
            "- The access token remains valid in this case (although it will eventually expire automatically).\n"
            "\n"
        ),
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully."}, status=status.HTTP_200_OK
            )
        except ValidationError:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"error": "An error occurred during logout."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# ---------------------------- Password Management Endpoints ----------------------------


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        tags=["Auth - Password"],
        summary="Change Password",
        description=(
            "# Allows a logged-in user to change their password.\n"
            "\n"
            "- To use this endpoint, you first need to authorize yourself from the top of the Swagger UI page.\n"
            "\n"
            "- For validation, we specifically used the validate method in the serializer during the RegisterView process.\n"
            "\n"
        ),
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # Check the old password
        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set and save the new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    @extend_schema(
        tags=["Auth - Password"],
        summary="Forgot Password",
        description=(
            "# Sends a password reset link to the user's email.\n"
            "\n"
            "- First, the email is checked to see if it exists in the database. If it does not, an error is raised.\n"
            "\n"
            "- The email format is validated using EmailField.\n"
            "\n"
            "- The website URL and the sender's email address are configured in the settings under SITE_URL and DEFAULT_FROM_EMAIL.\n"
            "\n"
        ),
    )
    def post(self, request):
        # Validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = get_object_or_404(User, email=email)

        # Generate a secure token and set expiration time
        token = get_random_string(32)
        token_expiration = datetime.now() + timedelta(hours=1)  # 1-hour expiration

        # Save token and expiration to the user
        user.verification_token = token
        user.token_expiration = token_expiration
        user.save()

        # Generate reset password link
        reset_link = f"{settings.SITE_URL}/auth/api/reset-password/?token={token}"

        # Send reset password email
        subject = "Reset your password"
        message = f"Click the link to reset your password: {reset_link}\nThis link will expire in 1 hour."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

        return Response(
            {"message": "Password reset link sent."}, status=status.HTTP_200_OK
        )


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    @extend_schema(
        tags=["Auth - Password"],
        summary="Reset Password",
        description=(
            "# Resets the user's password using the provided token and new password.\n"
            "\n"
            "- This is used in cases where, unlike the ChangePasswordView, the previous password is not available. Instead, the user provides their email address, and a link containing a temporary token is sent to them. The user's identity is determined based on the token.\n"
            "\n"
            "- The user then enters a new password, which replaces their old password in the database.\n"
            "\n"
            "- The token is automatically retrieved from the query parameters of the request.\n"
            "\n"
            "- The password validation rules from the ChangePasswordView are applied to ensure the new passwords meet the required standards.\n"
            "\n"
        ),
    )
    def post(self, request, *args, **kwargs):
        # Validate the serializer data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the token from query_params
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"error": "Token is required in query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find the user associated with the token
        user = get_object_or_404(User, verification_token=token)

        # Check if the token is expired
        if user.token_expiration < now():
            return Response(
                {"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Set the new password
        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)

        # Clear the token and expiration
        user.verification_token = None
        user.token_expiration = None
        user.save()

        return Response(
            {"message": "Password reset successfully."}, status=status.HTTP_200_OK
        )


# ---------------------------- Profile Management Endpoints ----------------------------


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    @extend_schema(
        tags=["Auth - Profile"],
        summary="Get Profile",
        description=(
            "# Fetches the profile details of the logged-in user.\n"
            "\n"
            "- To use this endpoint, you first need to authorize yourself from the top of the Swagger UI page.\n"
            "\n"
        ),
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["Auth - Profile"],
    summary="Update Profile",
    description="Updates the profile information of the logged-in user.",
)
class UpdateProfileView(generics.UpdateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Profile updated successfully."}, status=status.HTTP_200_OK
        )
