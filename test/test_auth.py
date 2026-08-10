import pytest

from server.schemas import LoginRequest, RegisterRequest
from server.services import auth_service

TEST_PASSWORD = "Secure1!"


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": TEST_PASSWORD},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["email"] == "new@example.com"
    assert body["user"]["id"].startswith("usr_")
    assert body["user"]["role"] == "admin"
    assert body["token"]


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": TEST_PASSWORD},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": TEST_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "login@example.com"
    assert body["user"]["role"] == "admin"
    assert body["token"]


def test_login_invalid_credentials(client):
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": TEST_PASSWORD},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "WrongPass1!"},
    )

    assert response.status_code == 500


def test_register_duplicate_email_raises(mock_db):
    req = RegisterRequest(email="dup@example.com", password=TEST_PASSWORD)
    auth_service.register(mock_db, req)

    with pytest.raises(ValueError, match="Email already registered"):
        auth_service.register(mock_db, req)


def test_register_weak_password_raises(mock_db):
    req = RegisterRequest(email="weak@example.com", password="12345678")

    with pytest.raises(ValueError, match="Password must be 8\\+ chars"):
        auth_service.register(mock_db, req)


def test_login_invalid_credentials_raises(mock_db):
    req = RegisterRequest(email="svc@example.com", password=TEST_PASSWORD)
    auth_service.register(mock_db, req)

    with pytest.raises(ValueError, match="Invalid credentials"):
        auth_service.login(
            mock_db, LoginRequest(email="svc@example.com", password="WrongPass1!")
        )
