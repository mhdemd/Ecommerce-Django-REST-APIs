import pytest
from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_with_token(db):
    """ایجاد کاربر با توکن و تاریخ انقضای معتبر"""
    user = User.objects.create_user(
        username="expireduser",
        username="testuser",
        email="testuser@example.com",
        password="OldPassword123!",
        verification_token="valid-token",
        token_expiration=now() + timedelta(hours=1),
    )
    return user


@pytest.fixture
def expired_user_with_token(db):
    """ایجاد کاربر با توکن منقضی"""
    user = User.objects.create_user(
        email="expireduser@example.com",
        password="OldPassword123!",
        verification_token="expired-token",
        token_expiration=now() - timedelta(hours=1),
    )
    return user


@pytest.mark.django_db
def test_reset_password_success(api_client, user_with_token):
    url = reverse("reset-password")
    data = {"new_password": "NewPassword123!"}
    response = api_client.post(url, data, QUERY_STRING="token=valid-token")

    user_with_token.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Password reset successfully."
    assert user_with_token.check_password("NewPassword123!")
    assert user_with_token.verification_token is None
    assert user_with_token.token_expiration is None


@pytest.mark.django_db
def test_reset_password_missing_token(api_client):
    url = reverse("reset-password")
    data = {"new_password": "NewPassword123!"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Token is required in query parameters."


@pytest.mark.django_db
def test_reset_password_invalid_token(api_client):
    url = reverse("reset-password")
    data = {"new_password": "NewPassword123!"}
    response = api_client.post(url, data, QUERY_STRING="token=invalid-token")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["error"] == "User not found with the given token."


@pytest.mark.django_db
def test_reset_password_expired_token(api_client, expired_user_with_token):
    url = reverse("reset-password")
    data = {"new_password": "NewPassword123!"}
    response = api_client.post(url, data, QUERY_STRING="token=expired-token")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"] == "Token has expired."


@pytest.mark.django_db
def test_reset_password_invalid_password(api_client, user_with_token):
    url = reverse("reset-password")
    data = {"new_password": "short"}  # رمز عبور کوتاه و نامعتبر
    response = api_client.post(url, data, QUERY_STRING="token=valid-token")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "new_password" in response.data
