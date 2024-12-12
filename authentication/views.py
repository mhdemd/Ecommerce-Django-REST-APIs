import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.models import Session
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from authentication.models import Session, User
from authentication.serializers import Disable2FASerializer
from authentication.tasks import (
    send_otp_via_email,
    send_otp_via_sms,
    send_reset_password_email,
    send_verification_email,
)

from .models import SessionInfo
from .serializers import (
    ChangePasswordSerializer,
    Disable2FASerializer,
    Enable2FASerializer,
    ForgotPasswordSerializer,
    GenerateOTPSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RegisterSerializer,
    ResendEmailSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    VerifyOTPSerializer,
)
from .tasks import send_otp_via_email, send_otp_via_sms
from .utils_otp_and_tokens import (
    delete_otp_for_user,
    get_otp_for_user,
    store_otp_for_user,
)

logger = logging.getLogger(__name__)


# ---------------------------- Mixin ----------------------------
class TokenMixin:
    def generate_token(self, user, expiry_hours=1):
        """
        Generate a secure token and save it to the user model with an expiration time.
        """
        # Generate the token
        token = get_random_string(32)
        token_expiration = now() + timedelta(hours=expiry_hours)

        # Log the token generation process
        logger.info(
            f"Generating token for user {user.id} with expiration at {token_expiration}."
        )

        # Save the token and expiration time to the user's model
        user.verification_token = token
        user.token_expiration = token_expiration
        user.save()

        logger.info(
            f"Token for user {user.id} saved successfully with expiration at {token_expiration}."
        )

        return token


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
        # Log the incoming registration request
        logger.info("Received registration request.")

        # Validate the incoming data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the new user
        user = serializer.save()
        logger.info(
            f"User {user.username} registered successfully with email {user.email}."
        )

        # Generate token using the mixin
        token = self.generate_token(user)
        logger.info(f"Generated verification token for user {user.username}.")

        # Create a verification link
        verification_link = f"{settings.SITE_URL}/auth/api/verify-email/?token={token}"
        logger.info(f"Generated verification link: {verification_link}")

        # Send the verification email using Celery
        subject = "Email Verification"
        message = f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n\n{verification_link}\n\nThank you!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        # Call the Celery task
        send_verification_email.delay(subject, message, from_email, recipient_list)

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
            logger.warning("Token is missing in the request.")
            return Response(
                {"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(verification_token=token)
            logger.info(f"Found user {user.id} for token verification.")

            # Check if the token is expired
            if user.token_expiration < timezone.now():
                logger.warning(f"Token for user {user.id} has expired.")
                return Response(
                    {"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Activate the user and clear the token
            user.is_active = True
            user.verification_token = None  # Remove the token after verification
            user.token_expiration = None
            user.save()

            logger.info(f"User {user.id} email verified successfully.")
            return Response(
                {"message": "Email verified successfully."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            logger.error("Invalid token provided, user not found.")
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
        },
    )
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            logger.warning("Attempted logout without refresh token.")
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(
                f"Successfully logged out user by blacklisting refresh token: {refresh_token}"
            )
            return Response(
                {"message": "Logged out successfully."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.warning("Invalid token provided: %s", e)
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
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

        # Log the password change attempt
        logger.info(f"User {user.id} is attempting to change their password.")

        # Check the old password
        if not user.check_password(old_password):
            logger.warning(
                f"User {user.id} attempted to change password with incorrect old password."
            )
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set and save the new password
        user.set_password(new_password)
        user.save()

        # Log the successful password change
        logger.info(f"Password changed successfully for user {user.id}.")

        return Response(
            {"message": "Password changed successfully."}, status=status.HTTP_200_OK
        )


class ForgotPasswordView(TokenMixin, generics.GenericAPIView):
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
        logger.info("Received forgot password request.")

        # Validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        logger.info(f"Looking up user with email: {email}")

        user = get_object_or_404(User, email=email)
        logger.info(f"User found with email: {email}, ID: {user.id}")

        # Generate token using the mixin
        token = self.generate_token(user)
        logger.info(f"Generated reset token for user ID: {user.id}")

        # Generate reset password link
        reset_link = f"{settings.SITE_URL}/auth/api/reset-password/?token={token}"
        logger.info(f"Reset link generated: {reset_link}")

        # Send reset password email using Celery
        subject = "Reset your password"
        message = f"Click the link to reset your password: {reset_link}\nThis link will expire in 1 hour."

        # Call the Celery task
        send_reset_password_email.delay(
            subject, message, settings.DEFAULT_FROM_EMAIL, [email]
        )
        logger.info(f"Password reset email task queued for: {email}")

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
            logger.warning("Reset password attempt without token.")
            return Response(
                {"error": "Token is required in query parameters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find the user associated with the token
        try:
            user = get_object_or_404(User, verification_token=token)
            logger.info(f"Found user {user.id} for token reset.")
        except User.DoesNotExist:
            logger.error(f"No user found with the given token.")
            return Response(
                {"error": "User not found with the given token."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the token is expired
        if user.token_expiration < now():
            logger.warning(f"Token for user {user.id} has expired.")
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

        logger.info(f"Password reset successfully for user {user.id}.")
        return Response(
            {"message": "Password reset successfully."}, status=status.HTTP_200_OK
        )


class ResendEmailView(TokenMixin, generics.GenericAPIView):
    serializer_class = ResendEmailSerializer

    @extend_schema(
        tags=["Auth - Password"],
        summary="Resend Email",
        description=(
            "Resends an email for either verification or password reset.\n"
            "- If `email_type` is 'verification', a verification email is resent.\n"
            "- If `email_type` is 'reset_password', a password reset email is resent."
        ),
        request=ResendEmailSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "Email resent successfully.",
                    }
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "User not found."}
                },
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Invalid email type."}
                },
            },
        },
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        email_type = serializer.validated_data["email_type"]

        try:
            user = User.objects.get(email=email)
            logger.info(f"User found with email: {email}, ID: {user.id}")
        except User.DoesNotExist:
            logger.error(f"User with email {email} not found.")
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if email_type == "verification":
            if user.is_active:
                logger.warning(f"User {user.id} is already verified.")
                return Response(
                    {"error": "User is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate verification token and link
            token = self.generate_token(user)
            verification_link = (
                f"{settings.SITE_URL}/auth/api/verify-email/?token={token}"
            )
            subject = "Email Verification"
            message = (
                f"Hi {user.username},\n\n"
                f"Please verify your email by clicking the link below:\n\n{verification_link}\n\nThank you!"
            )

            # Use Celery task for sending verification email
            send_verification_email.delay(
                subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
            )
            logger.info(f"Verification email task queued for {user.email}.")

            return Response(
                {"message": "Verification email resent successfully."},
                status=status.HTTP_200_OK,
            )

        elif email_type == "reset_password":
            # Generate reset token and link
            token = self.generate_token(user)
            reset_link = f"{settings.SITE_URL}/auth/api/reset-password/?token={token}"
            subject = "Reset your password"
            message = (
                f"Hi {user.username},\n\n"
                f"Click the link below to reset your password:\n\n{reset_link}\n\n"
                f"This link will expire in 1 hour."
            )

            # Use Celery task for sending reset password email
            send_reset_password_email.delay(
                subject, message, settings.DEFAULT_FROM_EMAIL, [user.email]
            )
            logger.info(f"Password reset email task queued for {user.email}.")

            return Response(
                {"message": "Password reset email resent successfully."},
                status=status.HTTP_200_OK,
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
            403: {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "User account is disabled.",
                    }
                },
            },
        },
    )
    def get(self, request, *args, **kwargs):
        # Check if the user is active
        if not request.user.is_active:
            logger.warning(
                f"User {request.user.id} attempted to access profile while inactive."
            )
            raise PermissionDenied("User account is disabled.")

        # Log the profile fetch attempt
        logger.info(f"User {request.user.id} is fetching their profile.")

        # Serialize and return the user profile data
        serializer = self.get_serializer(request.user)
        logger.info(f"Profile fetched successfully for user {request.user.id}.")
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
        user = self.request.user
        logger.info(f"Fetching profile for user {user.id}")
        return user

    def update(self, request, *args, **kwargs):
        # Custom behavior for better error management or logging if needed
        logger.info(f"Attempting to update profile for user {request.user.id}")
        response = super().update(request, *args, **kwargs)

        # Log the successful update
        logger.info(f"Profile updated successfully for user {request.user.id}")

        return Response(
            {"message": "Profile updated successfully."}, status=status.HTTP_200_OK
        )


# ---------------------------- OTP Endpoints ----------------------------
# ---------------------------- Enable 2FA ----------------------------
@extend_schema(
    tags=["Auth - OTP"],
    summary="Enable 2FA",
    description="Enables two-factor authentication (2FA) for the user using the specified method (email or SMS).",
)
class Enable2FAView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = Enable2FASerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        user = request.user

        if user.is_2fa_enabled:
            return Response(
                {"error": "2FA is already enabled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enable 2FA and save the selected method
        user.is_2fa_enabled = True
        user.two_fa_method = method
        user.save()

        return Response(
            {"message": f"2FA has been enabled using {method}."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Auth - OTP"],
    summary="Generate OTP",
    description="Generates a one-time password (OTP) for the user, which is sent via the selected method (email or SMS).",
)
class GenerateOTPView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GenerateOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        method = serializer.validated_data["method"]
        user = request.user

        # Check if 2FA is enabled and the method matches
        if not user.is_2fa_enabled or user.two_fa_method != method:
            return Response(
                {"error": "2FA is not enabled or method mismatch."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate OTP
        otp = get_random_string(6, allowed_chars="0123456789")
        # Store OTP in Redis with a TTL of 5 minutes
        store_otp_for_user(user.id, otp, ttl=300)

        # Send OTP via selected method
        if method == "email":
            send_otp_via_email.delay(
                "Your OTP Code",
                f"Your OTP code is: {otp}. It will expire in 5 minutes.",
                "no-reply@example.com",
                [user.email],
            )
        elif method == "sms":
            send_otp_via_sms.delay(user.phone_number, otp)

        return Response(
            {"message": f"OTP sent via {method}."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Auth - OTP"],
    summary="Verify OTP",
    description="Verifies the one-time password (OTP) entered by the user.",
)
class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        otp = serializer.validated_data["otp"]

        # Check if OTP is valid
        if not user.otp_code or user.otp_expiry < now() or user.otp_code != otp:
            return Response(
                {"error": "Invalid or expired OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # OTP is valid, clear it
        user.otp_code = None
        user.otp_expiry = None
        user.save()

        return Response(
            {"message": "OTP verified successfully."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Auth - OTP"],
    summary="Disable 2FA",
    description="Disables two-factor authentication (2FA) for the user after verifying the password.",
)
class Disable2FAView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = Disable2FASerializer

    def post(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if 2FA is enabled
        if not user.is_2fa_enabled:
            return Response(
                {"error": "2FA is not enabled."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Verify password or OTP
        if not user.check_password(serializer.validated_data["password"]):
            return Response(
                {"error": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Disable 2FA
        user.is_2fa_enabled = False
        user.two_fa_method = None
        user.otp_code = None
        user.otp_expiry = None
        user.save()

        return Response(
            {"message": "2FA has been disabled successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------- Sessions Endpoints ----------------------------
@extend_schema(
    tags=["Auth - Session"],
    summary="List Active Sessions",
    description="Fetches a list of all active sessions for the authenticated user.",
)
class ListSessionsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Retrieve all SessionInfo instances linked to the authenticated user
        session_infos = SessionInfo.objects.filter(user=request.user)

        session_data = []
        for session_info in session_infos:
            session = session_info.session  # Access the related Session object
            session_data.append(
                {
                    "session_key": session.session_key,
                    "device": session_info.device or "Unknown Device",
                    "location": session_info.location or "Unknown Location",
                    "created_at": session_info.session.expire_date,  # Adjust as needed
                    "last_activity": session_info.last_activity,
                }
            )

        return Response({"sessions": session_data}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Auth - Session"],
    summary="Delete a Specific Session",
    description="Deletes a specific session of the authenticated user by session key.",
)
class DeleteSessionView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_key):
        try:
            # Retrieve the SessionInfo linked to the given session_key and user
            session_info = SessionInfo.objects.get(
                session__session_key=session_key, user=request.user
            )
        except SessionInfo.DoesNotExist:
            return Response(
                {"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Delete the associated Session object, which will also delete SessionInfo due to CASCADE
        session_info.session.delete()

        return Response(
            {"message": "Session deleted successfully."}, status=status.HTTP_200_OK
        )


@extend_schema(
    tags=["Auth - Session"],
    summary="Logout from All Sessions",
    description="Logs out the user from all active sessions.",
)
class LogoutAllSessionsView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Retrieve all SessionInfo instances linked to the authenticated user
        session_infos = SessionInfo.objects.filter(user=request.user)

        # Count the sessions linked to the user
        session_count = session_infos.count()

        # Delete all associated Session objects
        session_keys = session_infos.values_list("session__session_key", flat=True)
        Session.objects.filter(session_key__in=session_keys).delete()

        # Delete the SessionInfo entries
        session_infos.delete()

        return Response(
            {"message": f"All {session_count} sessions logged out successfully."},
            status=status.HTTP_200_OK,
        )
