from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    ForgotPasswordView,
    LogoutView,
    ProfileView,
    RegisterView,
    ResendEmailView,
    ResetPasswordView,
    UpdateProfileView,
    VerifyEmailView,
)

urlpatterns = [
    # JWT endpoints
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"),
    # Authentication endpoints
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("api/reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("api/resend-email/", ResendEmailView.as_view(), name="resend_email"),
    # User management
    path("api/profile/", ProfileView.as_view(), name="profile"),
    path("api/profile/update/", UpdateProfileView.as_view(), name="update_profile"),
    path("api/change-password/", ChangePasswordView.as_view(), name="change_password"),
]
