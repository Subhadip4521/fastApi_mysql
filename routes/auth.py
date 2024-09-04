from datetime import timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config.constants import (
    ERROR_SIGNUP,
    ERROR_LOGIN,
    ERROR_LOGIN_PROCESS,
    SUCCESS_SIGNUP,
    SUCCESS_LOGIN,
    SUCCESS_LOGOUT,
    API_PREFIX,
)
from config.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.auth import TokenData, LoginSchema, ResponseModel
from schemas.user import User as UserSchema, UserCreate
from utils.authentication import verify_password, get_password_hash, create_access_token
from repositories.user import get_user_by_email
from services.user import create_user
from utils.dependencies import get_db, get_current_user

auth = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@auth.post(f"{API_PREFIX}/signup", response_model=ResponseModel)
async def signup(user: UserCreate, db: Session = Depends(get_db)) -> ResponseModel:
    try:
        existing_user = get_user_by_email(db, user.email)
        if existing_user:
            return ResponseModel(status=False, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        create_user(db, user, hashed_password) # type: ignore
        new_user = get_user_by_email(db, user.email)
        return ResponseModel(
            status=True,
            detail=SUCCESS_SIGNUP,
            data=dict(UserSchema(**dict(new_user))), # type: ignore
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail=ERROR_SIGNUP,
        )


@auth.post(f"{API_PREFIX}/login", response_model=ResponseModel)
async def login(user: LoginSchema, db: Session = Depends(get_db)):
    try:
        db_user = get_user_by_email(db, user.email)

        if not db_user or not verify_password(user.password, db_user.password):
            return ResponseModel(
                status=False,
                detail=ERROR_LOGIN,
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.user_id}, expires_delta=access_token_expires
        )

        return ResponseModel(
            status=True,
            detail=SUCCESS_LOGIN,
            data={"access_token": access_token, "token_type": "Bearer"},
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail=ERROR_LOGIN_PROCESS,
        )


@auth.post(f"{API_PREFIX}/logout", response_model=ResponseModel)
async def logout(current_user: TokenData = Depends(get_current_user)):
    return ResponseModel(status=True, detail=SUCCESS_LOGOUT)
