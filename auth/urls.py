from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    ProfileView,
    UpdateProfileView,
    ChangePasswordView,
)

urlpatterns = [
    # JWT endpoints
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    
    # Authentication endpoints
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/verify-email/", VerifyEmailView.as_view(), name="verify_email"),  
    path("api/login/", LoginView.as_view(), name="login"), 
    path("api/logout/", LogoutView.as_view(), name="logout"), 
    path("api/forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"), 
    path("api/reset-password/", ResetPasswordView.as_view(), name="reset_password"), 

    # User management
    path("api/profile/", ProfileView.as_view(), name="profile"), 
    path("api/profile/update/", UpdateProfileView.as_view(), name="update_profile"), 
    path("api/change-password/", ChangePasswordView.as_view(), name="change_password"), 
]
