from typing import Tuple

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLogin, UserRegister, UserResponse


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def register_user(self, user_in: UserRegister) -> UserResponse:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        hashed_pwd = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_pwd,
            full_name=user_in.full_name
        )
        created_user = await self.user_repo.create(new_user)
        return UserResponse.model_validate(created_user)

    async def authenticate_user(self, cred: UserLogin) -> Tuple[UserResponse, str, str]:
        user = await self.user_repo.get_by_email(cred.email)
        if not user or not verify_password(cred.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return UserResponse.model_validate(user), access_token, refresh_token
