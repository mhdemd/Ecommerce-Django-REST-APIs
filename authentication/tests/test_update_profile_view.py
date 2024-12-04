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
def user():
    user = User.objects.create_user(
        username="johndoe",
        email="johndoe@example.com",
        password="password123",
        first_name="John",
        last_name="Doe",
    )
    return user


@pytest.fixture
def another_user():
    user = User.objects.create_user(
        username="janedoe",
        email="janedoe@example.com",
        password="password123",
        first_name="Jane",
        last_name="Doe",
    )
    return user


@pytest.mark.django_db
def test_update_profile_success(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("update_profile")
    data = {
        "username": "johnupdated",
        "email": "johnupdated@example.com",
        "first_name": "John Updated",
        "last_name": "Doe Updated",
    }

    response = api_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Profile updated successfully."

    user.refresh_from_db()
    assert user.username == "johnupdated"
    assert user.email == "johnupdated@example.com"
    assert user.first_name == "John Updated"
    assert user.last_name == "Doe Updated"


@pytest.mark.django_db
def test_update_profile_unauthenticated(api_client):
    url = reverse("update_profile")
    data = {
        "username": "unauthuser",
        "email": "unauth@example.com",
        "first_name": "Unauth",
        "last_name": "User",
    }

    response = api_client.put(url, data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data
    assert response.data["detail"] == "Authentication credentials were not provided."


@pytest.mark.django_db
def test_update_profile_duplicate_email(api_client, user, another_user):
    api_client.force_authenticate(user=user)
    url = reverse("update_profile")
    data = {
        "username": "newusername",
        "email": another_user.email,
        "first_name": "John",
        "last_name": "Doe",
    }

    response = api_client.put(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data
    assert response.data["email"][0] == "This email is already in use."


@pytest.mark.django_db
def test_update_profile_duplicate_username(api_client, user, another_user):
    api_client.force_authenticate(user=user)
    url = reverse("update_profile")
    data = {
        "username": another_user.username,  # Using another user's username
        "email": "newemail@example.com",
        "first_name": "John",
        "last_name": "Doe",
    }

    response = api_client.put(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.data
    assert (
        str(response.data["username"][0]) == "A user with that username already exists."
    )  # Match the actual error message


@pytest.mark.django_db
def test_update_profile_html_injection(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("update_profile")
    data = {
        "username": "alert_XSS_",
        "email": "cleanemail@example.com",
        "first_name": "<b>John</b>",  # Input with HTML
        "last_name": "<i>Doe</i>",  # Input with HTML
    }

    response = api_client.put(url, data)

    # Ensure the response is rejected
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # Ensure the correct error messages are returned
    assert "first_name" in response.data
    assert "last_name" in response.data
    assert response.data["first_name"][0] == "Input contains invalid HTML or scripts."
    assert response.data["last_name"][0] == "Input contains invalid HTML or scripts."
