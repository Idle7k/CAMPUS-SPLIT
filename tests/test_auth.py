import pytest
from app.models.user import User, UserRole
from app.services import auth_service
from tests.conftest import get_form_csrf_token


def test_password_hashing():
    """Verify Argon2id hashing and verification logic."""
    password = "secret_password_123"
    hashed = auth_service.hash_password(password)

    # Hash must not match plaintext
    assert hashed != password
    assert hashed.startswith("$argon2id$")

    # Verification must succeed for correct password
    assert auth_service.verify_password(password, hashed) is True
    # Verification must fail for wrong password
    assert auth_service.verify_password("wrong_password", hashed) is False


def test_user_registration_service(db_session):
    """Test user registration service function."""
    user = auth_service.register_user(
        db=db_session,
        username="new_student",
        password="secure_password",
        role=UserRole.STUDENT,
    )
    assert user.id is not None
    assert user.username == "new_student"
    assert user.role == UserRole.STUDENT
    assert user.is_active is True
    assert auth_service.verify_password("secure_password", user.password_hash) is True


def test_user_registration_duplicate_rejected(db_session):
    """Ensure duplicate username registration raises ValueError."""
    auth_service.register_user(db_session, "duplicate_user", "pass123")
    with pytest.raises(ValueError, match="already taken"):
        auth_service.register_user(db_session, "duplicate_user", "different_pass")


def test_user_registration_short_password(db_session):
    """Ensure short passwords are rejected."""
    with pytest.raises(ValueError, match="at least 6 characters"):
        auth_service.register_user(db_session, "short_user", "123")


def test_authenticate_user_service(db_session):
    """Test authentication service."""
    auth_service.register_user(db_session, "auth_user", "valid_password")

    # Correct credentials
    user = auth_service.authenticate_user(db_session, "auth_user", "valid_password")
    assert user is not None
    assert user.username == "auth_user"

    # Incorrect password
    assert auth_service.authenticate_user(db_session, "auth_user", "wrong_password") is None

    # Non-existent user
    assert auth_service.authenticate_user(db_session, "nonexistent", "valid_password") is None


def test_http_login_success(client, test_student_user):
    """Test HTTP login endpoint sets session cookie and redirects to dashboard."""
    csrf_token = get_form_csrf_token(client, "/login")
    response = client.post(
        "/login",
        data={
            "username": test_student_user.username,
            "password": "student_pass123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/dashboard"
    assert "campus_split_session" in client.cookies


def test_http_login_invalid_credentials(client, test_student_user):
    """Test HTTP login with bad credentials returns 401 with error message."""
    csrf_token = get_form_csrf_token(client, "/login")
    response = client.post(
        "/login",
        data={
            "username": test_student_user.username,
            "password": "wrong_password",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 401
    assert "Invalid username or password" in response.text


def test_http_register_success(client):
    """Test HTTP registration endpoint creates account and signs in."""
    csrf_token = get_form_csrf_token(client, "/register")
    response = client.post(
        "/register",
        data={
            "username": "web_registered_student",
            "password": "new_secure_pass",
            "confirm_password": "new_secure_pass",
            "role": "student",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["Location"] == "/dashboard"
    assert "campus_split_session" in client.cookies


def test_http_register_mismatched_passwords(client):
    """Test mismatched password confirmation fails."""
    csrf_token = get_form_csrf_token(client, "/register")
    response = client.post(
        "/register",
        data={
            "username": "mismatch_student",
            "password": "password_one",
            "confirm_password": "password_two",
            "role": "student",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "Passwords do not match" in response.text


def test_http_logout(authenticated_student_client):
    """Test logout clears session and redirects to /login."""
    response = authenticated_student_client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["Location"] == "/login"

    # Attempting to access protected dashboard after logout should redirect to /login
    dash_response = authenticated_student_client.get("/dashboard", follow_redirects=False)
    assert dash_response.status_code == 303
    assert dash_response.headers["Location"] == "/login"
