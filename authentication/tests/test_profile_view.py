import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_user():
    user = User.objects.create_user(
        username="johndoe",
        email="johndoe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
    )
    return user


@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        username="inactiveuser",
        email="inactive@example.com",
        password="password123",
        first_name="Inactive",
        last_name="User",
        is_active=False,
    )
    return user


@pytest.mark.django_db
def test_get_profile_success(api_client, authenticated_user):
    url = reverse("profile")
    api_client.force_authenticate(user=authenticated_user)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == authenticated_user.id
    assert response.data["username"] == authenticated_user.username
    assert response.data["email"] == authenticated_user.email
    assert response.data["first_name"] == authenticated_user.first_name
    assert response.data["last_name"] == authenticated_user.last_name


@pytest.mark.django_db
def test_get_profile_unauthenticated(api_client):
    url = reverse("profile")

    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_get_profile_inactive_user(api_client, inactive_user):
    url = reverse("profile")
    api_client.force_authenticate(user=inactive_user)

    response = api_client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "detail" in response.data
    assert response.data["detail"] == "User account is disabled."
