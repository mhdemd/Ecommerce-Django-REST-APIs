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


def delete_otp_for_user(user_id):
    # Delete OTP after verification
    key = f"otp:{user_id}"
    delete_from_redis(key)


def store_verification_token(token, user_id, ttl=3600):
    # Store a verification token associated with a user_id for 1 hour
    key = f"verification_token:{token}"
    save_to_redis(key, user_id, ttl=ttl)


def get_user_id_by_verification_token(token):
    # Retrieve user_id associated with this token
    key = f"verification_token:{token}"
    return get_from_redis(key)
