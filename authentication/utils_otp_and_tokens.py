import random
import uuid

from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta

from .redis_utils import delete_from_redis, get_from_redis, save_to_redis


def generate_otp():
    # Generate a 6-digit numeric OTP
    return f"{random.randint(100000, 999999)}"
