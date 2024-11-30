from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    verification_token = models.CharField(max_length=32, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
