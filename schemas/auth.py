from typing import Optional, Any
from pydantic import BaseModel


class ResponseModel(BaseModel):
    status: bool
    detail: Optional[str] = None
    data: Optional[Any] = None


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    user_id: int | None = None

    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True
