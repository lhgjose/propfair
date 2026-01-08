from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from propfair_api.database import get_db_session
from propfair_api.schemas.auth import (
    UserRegister,
    UserLogin,
    Token,
    UserResponse,
)
from propfair_api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db_session),
) -> UserResponse:
    # TODO: Implement actual user creation
    return UserResponse(
        id="mock-user-id",
        email=user_data.email,
        name=user_data.name,
    )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: Session = Depends(get_db_session),
) -> Token:
    # TODO: Implement actual login
    access_token = create_access_token({"sub": "mock-user-id", "email": user_data.email})
    refresh_token = create_refresh_token({"sub": "mock-user-id"})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=None,
    )
