from datetime import datetime, timedelta, timezone

import jwt

from server.auth import (
    ALGORITHM,
    check_password,
    create_token,
    hash_password,
    verify_token,
)
from server.config import settings


def test_hash_and_verify_password():
    hashed = hash_password("Secure1!")

    assert hashed != "Secure1!"
    assert check_password("Secure1!", hashed)
    assert not check_password("wrong-password", hashed)


def test_create_and_verify_token():
    token = create_token("usr_abc", "cmp_xyz", "user@example.com")
    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "usr_abc"
    assert payload["company_id"] == "cmp_xyz"
    assert payload["email"] == "user@example.com"


def test_verify_token_rejects_expired_token():
    payload = {
        "sub": "usr_abc",
        "company_id": "cmp_xyz",
        "email": "user@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)

    assert verify_token(token) is None


def test_verify_token_rejects_invalid_token():
    assert verify_token("not-a-valid-token") is None
