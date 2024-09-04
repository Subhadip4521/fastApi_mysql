from sqlalchemy import text
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserUpdateRequest
from utils.authentication import get_password_hash


def get_user_by_email(db: Session, email: str):
    return (
        db.execute(text("CALL GetUserByEmail(:email)"), {"email": email})
        .mappings()
        .first()
    )


def get_user_by_id(db: Session, user_id: int):
    return (
        db.execute(text("CALL GetUserById(:userId)"), {"userId": user_id})
        .mappings()
        .first()
    )
