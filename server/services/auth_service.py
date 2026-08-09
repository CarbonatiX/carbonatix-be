import re

from auth import check_password, create_token, hash_password
from models import create_company, create_user, find_user_by_email
from schemas import AuthResponse, LoginRequest, RegisterRequest, UserBrief


def _validate_password(password: str) -> bool:
    return (
        len(password) >= 8
        and bool(re.search(r"[a-zA-Z]", password))
        and bool(re.search(r"\d", password))
        and bool(re.search(r"[^a-zA-Z0-9]", password))
    )


def register(db, req: RegisterRequest) -> AuthResponse:
    existing = find_user_by_email(db, req.email)
    if existing:
        raise ValueError("Email already registered")
    if not _validate_password(req.password):
        raise ValueError("Password must be 8+ chars with letters, numbers, and symbols")

    pw_hash = hash_password(req.password)
    company = create_company(db, owner_user_id="", name="My Company", technology="RKEF")
    user = create_user(db, req.email, pw_hash, company["id"], role="admin")
    db.companies.update_one(
        {"_id": company["id"]}, {"$set": {"owner_user_id": user["id"]}}
    )

    token = create_token(user["id"], company["id"], req.email, role="admin")
    return AuthResponse(
        user=UserBrief(id=user["id"], email=req.email, role="admin"),
        token=token,
    )


def login(db, req: LoginRequest) -> AuthResponse:
    user = find_user_by_email(db, req.email)
    if not user or not check_password(req.password, user["password_hash"]):
        raise ValueError("Invalid credentials")

    role = user.get("role", "admin")
    token = create_token(user["id"], user["company_id"], req.email, role=role)
    return AuthResponse(
        user=UserBrief(id=user["id"], email=req.email, role=role),
        token=token,
    )
