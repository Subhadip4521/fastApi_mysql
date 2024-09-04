from sqlalchemy.orm import Session
from sqlalchemy import text
from schemas.user import UserCreate, UserUpdateRequest
from utils.authentication import get_password_hash


def find_all_users(db: Session):
    result = db.execute(text("CALL GetAllUsers();"))
    return result.mappings().all()

def find_user_by_id(db: Session, user_id: int):
    result = db.execute(text("CALL GetUserById(:userId)"), {"userId": user_id})
    return result.mappings().first()

def create_user(db: Session, user: UserCreate):
    existing_user = (
        db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
        .mappings()
        .first()
    )
    if existing_user:
        return None

    hashed_password = get_password_hash(user.password)
    db.execute(
        text("CALL CreateUser(:name, :email, :password)"),
        {"name": user.name, "email": user.email, "password": hashed_password},
    )
    db.commit()
    return (
        db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
        .mappings()
        .first()
    )

def update_user(db: Session, user_update_request: UserUpdateRequest):
    hashed_password = (
        get_password_hash(user_update_request.password)
        if user_update_request.password
        else None
    )
    update_params = {
        "userId": user_update_request.user_id,
        "name": user_update_request.name,
        "email": user_update_request.email,
        "password": hashed_password,
    }
    db.execute(
        text("CALL UpdateUser(:userId, :name, :email, :password)"), update_params
    )
    db.commit()
    return (
        db.execute(
            text("CALL GetUserById(:userId)"), {"userId": user_update_request.user_id}
        )
        .mappings()
        .first()
    )

def delete_user(db: Session, user_id: int):
    db.execute(text("CALL DeleteUser(:userId)"), {"userId": user_id})
    db.commit()
    return {"user_id": user_id}
