import random

from django.utils.crypto import get_random_string

from .redis_utils import delete_from_redis, get_from_redis, save_to_redis


def generate_otp():
    """
    Generate a 6-digit numeric OTP.
    Returns:
        str: A string representing a 6-digit OTP code.
    """
    return f"{random.randint(100000, 999999)}"


def generate_verification_token():
    """
    Generate a random 32-character token for verification.
    Returns:
        str: A random 32-character alphanumeric string.
    """
    return get_random_string(32)


def store_otp_for_user(user_id, otp, ttl=300):
    """
    Store the given OTP for a user in Redis with a specified TTL.

    Args:
        user_id (int or str): The ID of the user.
        otp (str): The one-time password to store.
        ttl (int): Time-to-live in seconds (default 300 seconds).

    Returns:
        None
    """
    key = f"auth:otp:{user_id}"
    save_to_redis(key, otp, ttl=ttl)


def get_otp_for_user(user_id):
    """
    Retrieve the stored OTP for a given user from Redis.

    Args:
        user_id (int or str): The ID of the user.

    Returns:
        str or None: The stored OTP if it exists, otherwise None.
    """
    key = f"auth:otp:{user_id}"
    return get_from_redis(key)


def delete_otp_for_user(user_id):
    """
    Delete the stored OTP for a given user from Redis.

    Args:
        user_id (int or str): The ID of the user.

    Returns:
        None
    """
    key = f"auth:otp:{user_id}"
    delete_from_redis(key)


def store_verification_token(token, user_id, ttl=3600):
    """
    Store a verification token associated with a user_id for a specified TTL.

    Args:
        token (str): The verification token.
        user_id (int or str): The ID of the user associated with this token.
        ttl (int): Time-to-live in seconds (default 3600 seconds).

    Returns:
        None
    """
    key = f"auth:verification_token:{token}"
    save_to_redis(key, user_id, ttl=ttl)


def get_user_id_by_verification_token(token):
    """
    Retrieve the user_id associated with a given verification token from Redis.

    Args:
        token (str): The verification token.

    Returns:
        str or None: The user_id if the token is found, otherwise None.
    """
    key = f"auth:verification_token:{token}"
    return get_from_redis(key)


def delete_verification_token(token):
    """
    Delete a verification token from Redis.

    Args:
        token (str): The verification token to delete.

    Returns:
        None
    """
    key = f"auth:verification_token:{token}"
    delete_from_redis(key)


def store_password_reset_token(token, user_id, ttl=3600):
    """
    Store a password reset token associated with a user_id.

    Args:
        token (str): The password reset token.
        user_id (int or str): The ID of the user.
        ttl (int): Time-to-live in seconds (default 3600 seconds).

    Returns:
        None
    """
    key = f"auth:password_reset_token:{token}"
    save_to_redis(key, user_id, ttl=ttl)


def get_user_id_by_password_reset_token(token):
    """
    Retrieve the user_id associated with a password reset token.

    Args:
        token (str): The password reset token.

    Returns:
        str or None: The user_id if found, otherwise None.
    """
    key = f"auth:password_reset_token:{token}"
    return get_from_redis(key)


def delete_password_reset_token(token):
    """
    Delete a password reset token from Redis.

    Args:
        token (str): The password reset token to delete.

    Returns:
        None
    """
    key = f"auth:password_reset_token:{token}"
    delete_from_redis(key)
