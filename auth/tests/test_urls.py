import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# ---------------------------- Making fixtures ----------------------------

@pytest.fixture
def create_user():
    user = User.objects.create_user(username="testuser", password="testpassword")
    return user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def token(create_user):
    refresh = RefreshToken.for_user(create_user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

# ---------------------------- api/token/ ----------------------------

@pytest.mark.django_db
def test_token_obtain_pair(api_client, create_user):
    url = "/auth/api/token/"
    data = {"username": "testuser", "password": "testpassword"}
    response = api_client.post(url, data)
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_token_obtain_pair_invalid_credentials(api_client):
    url = "/auth/api/token/"
    data = {"username": "wronguser", "password": "wrongpassword"}
    response = api_client.post(url, data)
    assert response.status_code == 401
    assert "access" not in response.data
    assert "refresh" not in response.data


# ---------------------------- api/token/refresh/ ----------------------------

@pytest.mark.django_db
def test_token_refresh(api_client, token):
    url = "/auth/api/token/refresh/"
    data = {"refresh": token["refresh"]}
    response = api_client.post(url, data)
    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_token_refresh_invalid(api_client):
    url = "/auth/api/token/refresh/"
    data = {"refresh": "invalid_refresh_token"}
    response = api_client.post(url, data)
    assert response.status_code == 401
    assert "access" not in response.data

# ---------------------------- api/token/verify/ ----------------------------

@pytest.mark.django_db
def test_token_verify(api_client, token):
    url = "/auth/api/token/verify/"
    data = {"token": token["access"]}
    response = api_client.post(url, data)
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_verify_invalid(api_client):
    url = "/auth/api/token/verify/"
    data = {"token": "invalid_access_token"}
    response = api_client.post(url, data)
    assert response.status_code == 401
