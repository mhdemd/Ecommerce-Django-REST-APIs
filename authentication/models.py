from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session
from django.db import models
from django.utils.timezone import now


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

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


class SessionInfo(models.Model):
    session = models.OneToOneField(
        Session, on_delete=models.CASCADE, related_name="info"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="session_infos",
        null=True,  # Sessions might not always be tied to a user
    )
    device = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    last_activity = models.DateTimeField(default=now)

    def __str__(self):
        return f"SessionInfo for {self.user.username if self.user else 'Anonymous'} - {self.device or 'Unknown Device'}"
