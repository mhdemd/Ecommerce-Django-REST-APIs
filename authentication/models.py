from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    verification_token = models.CharField(max_length=32, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)

    # Fields for 2FA
    is_2fa_enabled = models.BooleanField(default=False)  # Whether 2FA is enabled
    two_fa_method = models.CharField(  # Method of 2FA (email or SMS)
        max_length=10,
        choices=[("email", "Email"), ("sms", "SMS")],
        blank=True,
        null=True,
    )
    otp_code = models.CharField(max_length=6, blank=True, null=True)  # OTP code
    otp_expiry = models.DateTimeField(blank=True, null=True)  # OTP expiration time
