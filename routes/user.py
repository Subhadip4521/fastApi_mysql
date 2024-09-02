from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config
from config.db import SessionLocal
from pydantic import BaseModel
from schemas.auth import Token, TokenData, LoginSchema, ResponseModel
from schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdateRequest,
    UserIdRequest,
)

user = APIRouter()

# Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings from environment variables
SECRET_KEY = config("SECRET_KEY", default="your_secret_key")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int
)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Helper Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode.get("sub", ""))
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
            )
        user_id = int(user_id_str)  # Convert to integer if necessary
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    result = db.execute(text("CALL GetUserById(:userId)"), {"userId": user_id})
    user = result.mappings().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return TokenData(user_id=user_id)


# Routes
@user.post("/signup", response_model=ResponseModel, tags=["AUTH"])
async def signup(user: UserCreate, db: Session = Depends(get_db)) -> ResponseModel:
    try:
        existing_user = (
            db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
            .mappings()
            .first()
        )
        if existing_user:
            return ResponseModel(status=False, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        db.execute(
            text("CALL CreateUser(:name, :email, :password)"),
            {"name": user.name, "email": user.email, "password": hashed_password},
        )
        db.commit()
        result = db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
        new_user = result.mappings().first()
        return ResponseModel(status=True, detail="User Signed Up Successfully.", data=dict(UserSchema(**dict(new_user))))  # type: ignore
    except Exception as e:
        return ResponseModel(
            status=False,
            detail="An error occurred during signup",
        )


@user.post("/login", response_model=ResponseModel, tags=["AUTH"])
async def login(user: LoginSchema, db: Session = Depends(get_db)):
    try:
        result = db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
        db_user = result.mappings().first()

        if not db_user or not verify_password(user.password, db_user.password):
            return ResponseModel(
                status=False,
                detail="Incorrect email or password",
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.user_id}, expires_delta=access_token_expires
        )

        return ResponseModel(
            status=True, detail="User Logged In Successfully.", data={"access_token": access_token, "token_type": "bearer"}
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail="An error occurred during login",
        )


@user.post("/logout", response_model=ResponseModel, tags=["AUTH"])
async def logout(current_user: TokenData = Depends(get_current_user)):
    # Handle logout logic, such as token invalidation if applicable
    return ResponseModel(status=True, detail="Logged out successfully")


@user.post("/find_all", response_model=ResponseModel, tags=["USERS"])
async def find_all_users(
    db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)
) -> ResponseModel:
    try:
        result = db.execute(text("CALL GetAllUsers();"))
        users = result.mappings().all()
        user_list = [UserSchema(**dict(user)) for user in users]
        return ResponseModel(
            status=True,
            detail="All the users fetched from database.",
            data={"users": user_list},
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail="An error occurred while fetching users",
        )


@user.post("/find_one", response_model=ResponseModel, tags=["USERS"])
async def find_one_user(
    request: UserIdRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        result = db.execute(
            text("CALL GetUserById(:userId)"), {"userId": request.user_id}
        )
        user = result.mappings().first()
        if not user:
            return ResponseModel(
                status=False, detail=f"User with user_id = {request.user_id} not found"
            )
        return ResponseModel(
            status=True,
            detail=f"User with user_id = {request.user_id} fetched from database.",
            data={"user": UserSchema(**dict(user))},
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail=f"An error occurred while fetching user with user_id = {request.user_id}: {str(e)}",
        )


@user.post("/create", response_model=ResponseModel, tags=["USERS"])
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        existing_user = (
            db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
            .mappings()
            .first()
        )
        if existing_user:
            return ResponseModel(status=False, detail="Email already registered")

        hashed_password = get_password_hash(user.password)
        db.execute(
            text("CALL CreateUser(:name, :email, :password)"),
            {"name": user.name, "email": user.email, "password": hashed_password},
        )
        db.commit()
        result = db.execute(text("CALL GetUserByEmail(:email)"), {"email": user.email})
        new_user = result.mappings().first()
        return ResponseModel(status=True, detail=f"User with user_id = {request.user_id} has been created.", data=dict(UserSchema(**dict(new_user))))  # type: ignore
    except Exception as e:
        return ResponseModel(
            status=False,
            detail="An error occurred during user creation",
        )


@user.post("/update", response_model=ResponseModel, tags=["USERS"])
async def update_user(
    user_update_request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        user_id = user_update_request.user_id
        hashed_password = (
            get_password_hash(user_update_request.password)
            if user_update_request.password
            else None
        )

        # Prepare the update parameters
        update_params = {
            "userId": user_id,
            "name": user_update_request.name,
            "email": user_update_request.email,
            "password": hashed_password,
        }

        # Execute the update operation
        db.execute(
            text("CALL UpdateUser(:userId, :name, :email, :password)"), update_params
        )
        db.commit()

        # Fetch the updated user data
        result = db.execute(text("CALL GetUserById(:userId)"), {"userId": user_id})
        updated_user = result.mappings().first()

        if not updated_user:
            return ResponseModel(
                status=False, detail=f"User with user_id = {user_id} not found"
            )

        return ResponseModel(
            status=True,
            detail=f"User with user_id = {user_id} has been updated successfully.",
            data=UserSchema(**dict(updated_user)), # type: ignore
        )
    except Exception as e:
        return ResponseModel(
            status=False, detail=f"An error occurred during user update: {str(e)}"
        )


@user.post("/delete", response_model=ResponseModel, tags=["USERS"])
async def delete_user(
    user_id_request: UserIdRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        user_id = user_id_request.user_id
        # Fetch the user details before deletion
        result = db.execute(text("CALL GetUserById(:userId)"), {"userId": user_id})
        user = result.mappings().first()

        if not user:
            return ResponseModel(
                status=False, detail=f"User with user_id = {user_id} not found"
            )

        # Perform the delete operation
        db.execute(text("CALL DeleteUser(:userId)"), {"userId": user_id})
        db.commit()

        # Return success response with details
        return ResponseModel(
            status=True,
            detail=f"User with user_id = {user_id} deleted successfully.",
            data={"user_id": user_id},
        )
    except Exception as e:
        return ResponseModel(
            status=False, detail=f"An error occurred during user deletion: {str(e)}"
        )
