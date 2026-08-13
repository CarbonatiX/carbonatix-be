from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.auth import verify_token
from server.database import get_db as _get_db

bearer_scheme = HTTPBearer()


def get_db():
    db = _get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return db


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db=Depends(get_db),
) -> dict:
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {"code": "unauthorized", "message": "Invalid or expired token"}
            },
        )
    user_id = payload.get("sub")
    company_id = payload.get("company_id")
    if not user_id or not company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {"code": "unauthorized", "message": "Invalid token payload"}
            },
        )
    return {
        "user_id": user_id,
        "company_id": company_id,
        "email": payload.get("email"),
        "role": payload.get("role", "admin"),
    }
