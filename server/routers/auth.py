from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from ..deps import get_db, get_current_user
from ..auth import (
    login as auth_login,
    register as auth_register,
    get_pending_users as auth_get_pending,
    approve_user as auth_approve,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    name: str
    password: str
    email: str = ""
    facility_id: str = ""


class TokenResponse(BaseModel):
    username: str
    name: str
    role: str
    token: str


class MessageResponse(BaseModel):
    message: str


class ApproveRequest(BaseModel):
    approved: bool


@router.post("/login")
def login(req: LoginRequest, db=Depends(get_db)):
    result = auth_login(db, req.username, req.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=result["error"]
        )
    return result


@router.post("/register", response_model=MessageResponse)
def register(req: RegisterRequest, db=Depends(get_db)):
    success, message = auth_register(db, req.username, req.name, req.password, req.email, req.facility_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    return {"message": message}


@router.get("/pending")
def get_pending_users(db=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.get("role") != "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya operator yang bisa melihat user pending"
        )
    users = auth_get_pending(db)
    return {"items": users, "total": len(users)}


@router.post("/approve/{user_id}")
def approve_user(user_id: str, req: ApproveRequest, db=Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.get("role") != "operator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya operator yang bisa menyetujui user"
        )
    success, message = auth_approve(db, user_id, req.approved)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )
    return {"message": message}
