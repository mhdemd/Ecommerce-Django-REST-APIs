import random
import uuid

from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta

from .redis_utils import delete_from_redis, get_from_redis, save_to_redis


def generate_otp():
    # Generate a 6-digit numeric OTP
    return f"{random.randint(100000, 999999)}"


def generate_verification_token():
    # Generate a random 32-char token
    return get_random_string(32)


def store_otp_for_user(user_id, otp, ttl=300):
    # Store OTP with TTL of 5 minutes for the given user_id
    key = f"otp:{user_id}"
    save_to_redis(key, otp, ttl=ttl)


def get_otp_for_user(user_id):
    # Retrieve OTP for the given user_id
    key = f"otp:{user_id}"
    return get_from_redis(key)
