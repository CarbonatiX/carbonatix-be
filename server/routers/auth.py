from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..deps import get_db
from ..auth import login as auth_login, register as auth_register

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    name: str
    password: str


class TokenResponse(BaseModel):
    username: str
    name: str
    role: str
    token: str


class MessageResponse(BaseModel):
    message: str


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db=Depends(get_db)):
    result = auth_login(db, req.username, req.password)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )
    return result


@router.post("/register", response_model=MessageResponse)
def register(req: RegisterRequest, db=Depends(get_db)):
    success, message = auth_register(db, req.username, req.name, req.password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    return {"message": message}