from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    name: str
    password: str


class UserResponse(BaseModel):
    username: str
    name: str
    role: str