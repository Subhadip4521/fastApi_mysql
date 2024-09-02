from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdateRequest(BaseModel):
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserIdRequest(BaseModel):
    user_id: int


class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True
