import logging
import random

from django.utils.crypto import get_random_string

from authentication.redis_utils import delete_from_redis, get_from_redis, save_to_redis

logger = logging.getLogger(__name__)


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
    try:
        logger.info(f"Attempting to store OTP for user {user_id}: {otp}")
        save_to_redis(key, otp, ttl=ttl)
        logger.info(f"Successfully stored OTP for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to store OTP for user {user_id}: {e}")
        raise


def get_otp_for_user(user_id):
    """
    Retrieve the stored OTP for a given user from Redis.

    Args:
        user_id (int or str): The ID of the user.

    Returns:
        str or None: The stored OTP if it exists, otherwise None.
    """
    key = f"auth:otp:{user_id}"
    try:
        logger.info(f"Attempting to retrieve OTP for user {user_id}")
        otp = get_from_redis(key)
        if otp:
            logger.info(f"Retrieved OTP for user {user_id}: {otp}")
        else:
            logger.warning(f"No OTP found for user {user_id}")
        return otp
    except Exception as e:
        logger.error(f"Failed to retrieve OTP for user {user_id}: {e}")
        raise


def delete_otp_for_user(user_id):
    """
    Delete the stored OTP for a given user from Redis.

    Args:
        user_id (int or str): The ID of the user.

    Returns:
        None
    """
    key = f"auth:otp:{user_id}"
    try:
        logger.info(f"Attempting to delete OTP for user {user_id}")
        delete_from_redis(key)
        logger.info(f"Successfully deleted OTP for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to delete OTP for user {user_id}: {e}")
        raise


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
    try:
        logger.info(f"Attempting to store verification token for user {user_id}")
        save_to_redis(key, user_id, ttl=ttl)
        logger.info(f"Successfully stored verification token for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to store verification token for user {user_id}: {e}")
        raise


def get_user_id_by_verification_token(token):
    """
    Retrieve the user_id associated with a given verification token from Redis.

    Args:
        token (str): The verification token.

    Returns:
        str or None: The user_id if the token is found, otherwise None.
    """
    key = f"auth:verification_token:{token}"
    try:
        logger.info(f"Attempting to retrieve user ID by verification token {token}")
        user_id = get_from_redis(key)
        if user_id:
            logger.info(f"Retrieved user ID {user_id} for token {token}")
        else:
            logger.warning(f"No user ID found for token {token}")
        return user_id
    except Exception as e:
        logger.error(f"Failed to retrieve user ID by token {token}: {e}")
        raise


def delete_verification_token(token):
    """
    Delete a verification token from Redis.

    Args:
        token (str): The verification token to delete.

    Returns:
        None
    """
    key = f"auth:verification_token:{token}"
    try:
        logger.info(f"Attempting to delete verification token {token}")
        delete_from_redis(key)
        logger.info(f"Successfully deleted verification token {token}")
    except Exception as e:
        logger.error(f"Failed to delete verification token {token}: {e}")
        raise


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
    try:
        logger.info(f"Attempting to store password reset token for user {user_id}")
        save_to_redis(key, user_id, ttl=ttl)
        logger.info(f"Successfully stored password reset token for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to store password reset token for user {user_id}: {e}")
        raise


def get_user_id_by_password_reset_token(token):
    """
    Retrieve the user_id associated with a password reset token.

    Args:
        token (str): The password reset token.

    Returns:
        str or None: The user_id if found, otherwise None.
    """
    key = f"auth:password_reset_token:{token}"
    try:
        logger.info(f"Attempting to retrieve user ID by password reset token {token}")
        user_id = get_from_redis(key)
        if user_id:
            logger.info(f"Retrieved user ID {user_id} for token {token}")
        else:
            logger.warning(f"No user ID found for token {token}")
        return user_id
    except Exception as e:
        logger.error(f"Failed to retrieve user ID by token {token}: {e}")
        raise


def delete_password_reset_token(token):
    """
    Delete a password reset token from Redis.

    Args:
        token (str): The password reset token to delete.

    Returns:
        None
    """
    key = f"auth:password_reset_token:{token}"
    try:
        logger.info(f"Attempting to delete password reset token {token}")
        delete_from_redis(key)
        logger.info(f"Successfully deleted password reset token {token}")
    except Exception as e:
        logger.error(f"Failed to delete password reset token {token}: {e}")
        raise
