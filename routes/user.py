from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.user import (
    create_user,
    delete_user,
    find_all_users,
    find_user_by_id,
    update_user,
)
from utils.dependencies import get_db, get_current_user
from config.constants import (
    ERROR_USER_FETCHING,
    ERROR_USER_NOT_FOUND,
    ERROR_CREATE_USER,
    ERROR_UPDATE_USER,
    ERROR_DELETE_USER,
    ERROR_USERS_FETCHING,
    SUCCESS_USER_CREATED,
    SUCCESS_USER_UPDATED,
    SUCCESS_USER_DELETED,
    SUCCESS_USERS_FETCHED,
    SUCCESS_USER_FETCHED,
    API_PREFIX,
)
from schemas.auth import TokenData, ResponseModel
from schemas.user import (
    User as UserSchema,
    UserCreate,
    UserUpdateRequest,
    UserIdRequest,
)

user = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@user.post(f"{API_PREFIX}/find_all", response_model=ResponseModel)
async def find_all_users_route(
    db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)
) -> ResponseModel:
    try:
        users = find_all_users(db)
        user_list = [UserSchema(**dict(user)) for user in users]
        return ResponseModel(
            status=True,
            detail=SUCCESS_USERS_FETCHED,
            data={"users": user_list},
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail=ERROR_USERS_FETCHING,
        )


@user.post(f"{API_PREFIX}/find_one", response_model=ResponseModel)
async def find_one_user_route(
    request: UserIdRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        user = find_user_by_id(db, request.user_id)
        if not user:
            return ResponseModel(status=False, detail=ERROR_USER_NOT_FOUND)
        return ResponseModel(
            status=True,
            detail=SUCCESS_USER_FETCHED.format(user_id=request.user_id),
            data={"user": UserSchema(**dict(user))},
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail=f"{ERROR_USER_FETCHING.format(user_id=request.user_id)}:{str(e)}",
        )


@user.post(f"{API_PREFIX}/create", response_model=ResponseModel)
async def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        new_user = create_user(db, user)
        if not new_user:
            return ResponseModel(status=False, detail="Email already registered")
        return ResponseModel(
            status=True,
            detail=SUCCESS_USER_CREATED.format(user_id=new_user["user_id"]),  # type: ignore
            data=dict(UserSchema(**dict(new_user))),  # type: ignore
        )
    except Exception as e:
        return ResponseModel(
            status=False,
            detail=ERROR_CREATE_USER,
        )


@user.post(f"{API_PREFIX}/update", response_model=ResponseModel)
async def update_user_route(
    user_update_request: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        updated_user = update_user(db, user_update_request)
        if not updated_user:
            return ResponseModel(status=False, detail=ERROR_USER_NOT_FOUND)
        return ResponseModel(
            status=True,
            detail=SUCCESS_USER_UPDATED.format(user_id=user_update_request.user_id),
            data=UserSchema(**dict(updated_user)),  # type: ignore
        )
    except Exception as e:
        return ResponseModel(status=False, detail=f"{ERROR_UPDATE_USER}: {str(e)}")


@user.post(f"{API_PREFIX}/delete", response_model=ResponseModel)
async def delete_user_route(
    user_id_request: UserIdRequest,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
) -> ResponseModel:
    try:
        result = delete_user(db, user_id_request.user_id)
        return ResponseModel(
            status=True,
            detail=SUCCESS_USER_DELETED.format(user_id=user_id_request.user_id),
            data=result,
        )
    except Exception as e:
        return ResponseModel(status=False, detail=f"{ERROR_DELETE_USER}: {str(e)}")
