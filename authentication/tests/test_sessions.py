import uuid

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from authentication.models import SessionInfo


@pytest.fixture
def api_client():
    """Fixture to provide API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Fixture to create a user for testing."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword",
    )


def create_session(user, device="Unknown Device", location="Unknown Location"):
    """Helper function to create a Session and update its SessionInfo."""
    # Generate a unique session key
    session_key = uuid.uuid4().hex

    # Create a Session object
    session = Session.objects.create(
        session_key=session_key,
        session_data="{}",  # Empty session data
        expire_date=timezone.now() + timezone.timedelta(days=1),
    )

    # Retrieve the automatically created SessionInfo instance
    try:
        session_info = SessionInfo.objects.get(session=session)
    except SessionInfo.DoesNotExist:
        pytest.fail("SessionInfo was not created by signal.")

    # Update SessionInfo fields
    session_info.user = user
    session_info.device = device
    session_info.location = location
    session_info.last_activity = timezone.now()
    session_info.save()

    return session


@pytest.mark.django_db
def test_list_sessions_success(api_client, create_user):
    """Test successful retrieval of active sessions."""
    user = create_user

    # Create some sessions
    session1 = create_session(user, device="Chrome", location="New York")
    session2 = create_session(user, device="Firefox", location="Los Angeles")

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Make GET request to list_sessions
    response = api_client.get(reverse("list_sessions"))

    assert response.status_code == 200
    assert "sessions" in response.data
    assert len(response.data["sessions"]) == 2

    # Verify session details
    session_keys = {session1.session_key, session2.session_key}
    returned_keys = {session["session_key"] for session in response.data["sessions"]}
    assert session_keys == returned_keys

    for session in response.data["sessions"]:
        if session["session_key"] == session1.session_key:
            assert session["device"] == "Chrome"
            assert session["location"] == "New York"
        elif session["session_key"] == session2.session_key:
            assert session["device"] == "Firefox"
            assert session["location"] == "Los Angeles"


@pytest.mark.django_db
def test_list_sessions_no_sessions(api_client, create_user):
    """Test listing sessions when user has no active sessions."""
    user = create_user

    # Ensure no sessions exist for the user
    assert SessionInfo.objects.filter(user=user).count() == 0

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Make GET request to list_sessions
    response = api_client.get(reverse("list_sessions"))

    assert response.status_code == 200
    assert "sessions" in response.data
    assert len(response.data["sessions"]) == 0


@pytest.mark.django_db
def test_list_sessions_unauthorized(api_client):
    """Test listing sessions without authentication."""
    # Make GET request without authentication
    response = api_client.get(reverse("list_sessions"))

    assert response.status_code == 401  # Unauthorized


@pytest.mark.django_db
def test_delete_session_success(api_client, create_user):
    """Test successful deletion of a specific session."""
    user = create_user
    session = create_session(user, device="Chrome", location="New York")

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Make POST request to delete_session
    response = api_client.post(reverse("delete_session", args=[session.session_key]))

    assert response.status_code == 200
    assert response.data["message"] == "Session deleted successfully."

    # Verify that the session and SessionInfo are deleted
    assert not Session.objects.filter(session_key=session.session_key).exists()
    assert not SessionInfo.objects.filter(session=session).exists()


@pytest.mark.django_db
def test_delete_session_not_found(api_client, create_user):
    """Test deletion of a non-existent session."""
    user = create_user

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Use a random session_key
    fake_session_key = uuid.uuid4().hex

    # Make POST request to delete_session
    response = api_client.post(reverse("delete_session", args=[fake_session_key]))

    assert response.status_code == 404
    assert response.data["error"] == "Session not found."


@pytest.mark.django_db
def test_delete_session_another_user_session(api_client, create_user):
    """Test attempting to delete another user's session."""
    user1 = create_user
    user2 = get_user_model().objects.create_user(
        username="otheruser",
        email="otheruser@example.com",
        password="otherpassword",
    )

    # Create a session for user2
    session = create_session(user2, device="Safari", location="Chicago")

    # Authenticate as user1
    api_client.force_authenticate(user=user1)

    # Attempt to delete user2's session
    response = api_client.post(reverse("delete_session", args=[session.session_key]))

    assert response.status_code == 404
    assert response.data["error"] == "Session not found."

    # Verify that the session still exists
    assert Session.objects.filter(session_key=session.session_key).exists()
    assert SessionInfo.objects.filter(session=session).exists()


@pytest.mark.django_db
def test_delete_session_unauthorized(api_client):
    """Test deleting a session without authentication."""
    # Use a random session_key
    fake_session_key = uuid.uuid4().hex

    # Make POST request without authentication
    response = api_client.post(reverse("delete_session", args=[fake_session_key]))

    assert response.status_code == 401  # Unauthorized


@pytest.mark.django_db
def test_delete_session_invalid_session_key(api_client, create_user):
    """Test deletion with an invalid session key format."""
    user = create_user

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Invalid session_key (not matching expected format)
    invalid_session_key = "invalid_key_format!"

    # Make POST request to delete_session
    response = api_client.post(reverse("delete_session", args=[invalid_session_key]))

    # Depending on implementation, this might return 404 or a validation error
    # Here, assuming it returns 404
    assert response.status_code == 404
    assert response.data["error"] == "Session not found."


@pytest.mark.django_db
def test_logout_all_sessions_success(api_client, create_user):
    """Test successful logout from all sessions."""
    user = create_user

    # Create multiple sessions
    session1 = create_session(user, device="Chrome", location="New York")
    session2 = create_session(user, device="Firefox", location="Los Angeles")

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Make POST request to logout_all_sessions
    response = api_client.post(reverse("logout_all_sessions"))

    assert response.status_code == 200
    assert response.data["message"] == "All 2 sessions logged out successfully."

    # Verify that all sessions and SessionInfos are deleted
    assert not Session.objects.filter(session_key=session1.session_key).exists()
    assert not SessionInfo.objects.filter(session=session1).exists()
    assert not Session.objects.filter(session_key=session2.session_key).exists()
    assert not SessionInfo.objects.filter(session=session2).exists()


@pytest.mark.django_db
def test_logout_all_sessions_no_sessions(api_client, create_user):
    """Test logout when the user has no active sessions."""
    user = create_user

    # Ensure no sessions exist for the user
    assert SessionInfo.objects.filter(user=user).count() == 0

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Make POST request to logout_all_sessions
    response = api_client.post(reverse("logout_all_sessions"))

    assert response.status_code == 200
    assert response.data["message"] == "All 0 sessions logged out successfully."


@pytest.mark.django_db
def test_logout_all_sessions_unauthorized(api_client):
    """Test logging out from all sessions without authentication."""
    # Make POST request without authentication
    response = api_client.post(reverse("logout_all_sessions"))

    assert response.status_code == 401  # Unauthorized


@pytest.mark.django_db
def test_list_sessions_with_expired_session(api_client, create_user):
    """Test that expired sessions are listed (assuming your system does not auto-clean)."""
    user = create_user

    # Create an expired session using helper function
    expired_session = create_session(
        user, device="Old Browser", location="Old Location"
    )
    # Manually set expire_date to past
    expired_session.expire_date = timezone.now() - timezone.timedelta(days=1)
    expired_session.save()

    # Update the corresponding SessionInfo
    session_info = SessionInfo.objects.get(session=expired_session)
    session_info.last_activity = timezone.now() - timezone.timedelta(days=2)
    session_info.save()

    # Create a valid session
    valid_session = create_session(user, device="Chrome", location="New York")

    # Authenticate the client
    api_client.force_authenticate(user=user)

    # Make GET request to list_sessions
    response = api_client.get(reverse("list_sessions"))

    assert response.status_code == 200
    assert "sessions" in response.data
    # Assuming expired sessions are still listed
    assert len(response.data["sessions"]) == 2
    session_keys = {expired_session.session_key, valid_session.session_key}
    returned_keys = {session["session_key"] for session in response.data["sessions"]}
    assert session_keys == returned_keys
