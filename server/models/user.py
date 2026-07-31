from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    operator = "operator"
    viewer = "viewer"


class UserStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole
    facility_id: str
    phone_number: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    facility_id: Optional[str] = None
    is_active: Optional[bool] = None


class UserApproval(BaseModel):
    status: UserStatus
    approved_by: str
    approved_at: datetime


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    facility_id: str
    phone_number: Optional[str] = None
    status: UserStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListParams(BaseModel):
    role: Optional[UserRole] = None
    facility_id: Optional[str] = None
    status: Optional[UserStatus] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    name: str
    password: str
