from unittest.mock import patch

import pytest

from authentication.utils_otp_and_tokens import (
    delete_otp_for_user,
    delete_password_reset_token,
    delete_verification_token,
    get_otp_for_user,
    get_user_id_by_password_reset_token,
    get_user_id_by_verification_token,
    store_otp_for_user,
    store_password_reset_token,
    store_verification_token,
)


@pytest.fixture
def mock_redis():
    """Mock the Redis functions used in the utils."""
    with patch("authentication.utils_otp_and_tokens.save_to_redis") as mock_save, patch(
        "authentication.utils_otp_and_tokens.get_from_redis"
    ) as mock_get, patch(
        "authentication.utils_otp_and_tokens.delete_from_redis"
    ) as mock_delete:
        yield mock_save, mock_get, mock_delete


def test_store_and_retrieve_otp(mock_redis):
    """Test storing and retrieving an OTP from Redis."""
    mock_save, mock_get, mock_delete = mock_redis

    user_id = 1
    otp = "123456"
    ttl = 300

    # Simulate successful retrieval
    mock_get.return_value = otp

    # Store OTP
    store_otp_for_user(user_id, otp, ttl)
    mock_save.assert_called_once_with(f"auth:otp:{user_id}", otp, ttl=ttl)

    # Retrieve OTP
    retrieved_otp = get_otp_for_user(user_id)
    mock_get.assert_called_once_with(f"auth:otp:{user_id}")
    assert retrieved_otp == otp, "Retrieved OTP does not match the stored value"


def test_delete_otp(mock_redis):
    """Test deleting an OTP from Redis."""
    mock_save, mock_get, mock_delete = mock_redis

    user_id = 1

    # Delete OTP
    delete_otp_for_user(user_id)
    mock_delete.assert_called_once_with(f"auth:otp:{user_id}")


def test_store_and_retrieve_verification_token(mock_redis):
    """Test storing and retrieving a verification token from Redis."""
    mock_save, mock_get, mock_delete = mock_redis

    token = "verification_token"
    user_id = 1
    ttl = 3600

    # Simulate successful retrieval
    mock_get.return_value = str(user_id)

    # Store verification token
    store_verification_token(token, user_id, ttl)
    mock_save.assert_called_once_with(
        f"auth:verification_token:{token}", user_id, ttl=ttl
    )

    # Retrieve user ID by token
    retrieved_user_id = get_user_id_by_verification_token(token)
    mock_get.assert_called_once_with(f"auth:verification_token:{token}")
    assert retrieved_user_id == str(
        user_id
    ), "Retrieved user ID does not match the stored value"


def test_delete_verification_token(mock_redis):
    """Test deleting a verification token from Redis."""
    mock_save, mock_get, mock_delete = mock_redis

    token = "verification_token"

    # Delete verification token
    delete_verification_token(token)
    mock_delete.assert_called_once_with(f"auth:verification_token:{token}")


def test_store_and_retrieve_password_reset_token(mock_redis):
    """Test storing and retrieving a password reset token from Redis."""
    mock_save, mock_get, mock_delete = mock_redis

    token = "reset_token"
    user_id = 1
    ttl = 3600

    # Simulate successful retrieval
    mock_get.return_value = str(user_id)

    # Store password reset token
    store_password_reset_token(token, user_id, ttl)
    mock_save.assert_called_once_with(
        f"auth:password_reset_token:{token}", user_id, ttl=ttl
    )

    # Retrieve user ID by token
    retrieved_user_id = get_user_id_by_password_reset_token(token)
    mock_get.assert_called_once_with(f"auth:password_reset_token:{token}")
    assert retrieved_user_id == str(
        user_id
    ), "Retrieved user ID does not match the stored value"


def test_delete_password_reset_token(mock_redis):
    """Test deleting a password reset token from Redis."""
    mock_save, mock_get, mock_delete = mock_redis

    token = "reset_token"

    # Delete password reset token
    delete_password_reset_token(token)
    mock_delete.assert_called_once_with(f"auth:password_reset_token:{token}")
