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
            "- The serializer includes built-in validations to prevent XSS attacks.\n"
            "- Email and password fields are validated.\n"
            "- Rate limiting is implemented.\n"
            "- 'verification_token' and 'token_expiration' fields secure the email verification link.\n"
            "- Token is cleared after verification."
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
        token_expiration = datetime.now() + timedelta(
            hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRY
        )  # Token valid for 1 hour

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
            "- When the user clicks on the link sent to their email, this API is called.\n"
            "- The link contains a temporary token that is valid for one hour.\n"
            "- Without the temporary token, you cannot access this API.\n"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Email verified successfully.",
                    }
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Invalid token.",
                    }
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Token has expired.",
                    }
                },
            },
        },
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
            "- You need to authorize yourself from the Swagger UI before accessing this endpoint.\n"
            "- Send the refresh token in the request body; it will be added to the blacklist and invalidated.\n"
            "- Note that the access token will remain valid until it expires.\n"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Logged out successfully.",
                    }
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Invalid token.",
                    }
                },
            },
            500: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "An error occurred during logout.",
                    }
                },
            },
        },
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
            "- To use this endpoint, you first need to authorize yourself from the top of the Swagger UI page.\n"
            "- For validation, we specifically used the validate method in the serializer during the RegisterView process.\n"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Password changed successfully.",
                    }
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Old password is incorrect."}
                },
            },
            422: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Password does not meet validation criteria.",
                    }
                },
            },
        },
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
            "- First, the email is checked to see if it exists in the database. If it does not, an error is raised.\n"
            "- The email format is validated using EmailField.\n"
            "- The website URL and the sender's email address are configured in the settings under SITE_URL and DEFAULT_FROM_EMAIL.\n"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Password reset link sent.",
                    }
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "User with this email does not exist.",
                    }
                },
            },
            422: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Invalid email format."}
                },
            },
        },
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
            "- This is used in cases where, unlike the ChangePasswordView, the previous password is not available. Instead, the user provides their email address, and a link containing a temporary token is sent to them. The user's identity is determined based on the token.\n"
            "- The user then enters a new password, which replaces their old password in the database.\n"
            "- The token is automatically retrieved from the query parameters of the request.\n"
            "- The password validation rules from the ChangePasswordView are applied to ensure the new passwords meet the required standards.\n"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Password reset successfully.",
                    }
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Token is required in query parameters.",
                    }
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "User not found with the given token.",
                    }
                },
            },
            422: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Token has expired."}
                },
            },
        },
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
            "- To use this endpoint, you first need to authorize yourself from the top of the Swagger UI page.\n"
        ),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "username": {"type": "string", "example": "johndoe"},
                    "email": {"type": "string", "example": "johndoe@example.com"},
                    "first_name": {"type": "string", "example": "John"},
                    "last_name": {"type": "string", "example": "Doe"},
                },
            },
            401: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Authentication credentials were not provided.",
                    }
                },
            },
        },
    )
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["Auth - Profile"],
    summary="Update Profile",
    description="# Updates the profile information of the logged-in user.",
    responses={
        200: {
            "description": "Profile updated successfully.",
            "content": {
                "application/json": {
                    "example": {"message": "Profile updated successfully."}
                }
            },
        },
        400: {
            "description": "Bad request. Validation errors or invalid data provided.",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid data provided.",
                        "details": {"field_name": ["error message"]},
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized. Authentication credentials were not provided or are invalid.",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication credentials were not provided."
                    }
                }
            },
        },
    },
)
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        # Fetch the authenticated user
        return self.request.user

    def update(self, request, *args, **kwargs):
        # Custom behavior for better error management or logging if needed
        response = super().update(request, *args, **kwargs)
        return Response(
            {"message": "Profile updated successfully."}, status=status.HTTP_200_OK
        )
