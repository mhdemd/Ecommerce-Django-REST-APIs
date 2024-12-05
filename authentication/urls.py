from django.urls import path

from .views import (
    ChangePasswordView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    DeleteSessionView,
    Disable2FAView,
    Enable2FAView,
    ForgotPasswordView,
    GenerateOTPView,
    ListSessionsView,
    LogoutAllSessionsView,
    LogoutView,
    ProfileView,
    RegisterView,
    ResendEmailView,
    ResetPasswordView,
    UpdateProfileView,
    VerifyEmailView,
    VerifyOTPView,
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
    # OTP and 2FA endpoints
    path("api/enable-2fa/", Enable2FAView.as_view(), name="enable_2fa"),
    path("api/generate-otp/", GenerateOTPView.as_view(), name="generate_otp"),
    path("api/verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("api/disable-2fa/", Disable2FAView.as_view(), name="disable_2fa"),
    # Sessions endpoints
    path("api/sessions/", ListSessionsView.as_view(), name="list_sessions"),
    path(
        "api/sessions/<int:session_id>/delete/",
        DeleteSessionView.as_view(),
        name="delete_session",
    ),
    path(
        "api/sessions/logout-all/",
        LogoutAllSessionsView.as_view(),
        name="logout_all_sessions",
    ),
]
