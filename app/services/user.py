from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from datetime import timedelta
from typing import Annotated

from jose import JWTError, jwt
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.daos.user import UserDao
from app.db import get_session
from app.models.user import User as UserModel
from app.schemas.token import Token, TokenData
from app.schemas.user import ChangePasswordIn, UserIn, UserOut
from app.services.utils import UtilsService, oauth2_scheme
from app.settings import settings


class UserService:
    @staticmethod
    async def register_user(user_data: UserIn, session: AsyncSession):
        user_exist = await UserService.user_email_exists(session, user_data.email)

        if user_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with the given email already exists!",
            )

        hashed_password = UtilsService.get_password_hash(user_data.password)
        new_user_data = user_data.model_dump()
        new_user_data.pop("password")
        new_user_data["password_hash"] = hashed_password
        new_user = await UserDao(session).create(new_user_data)
        logger.info(f"New user created successfully: {new_user}!")
        return JSONResponse(
            content={"message": "User created successfully"},
            status_code=status.HTTP_201_CREATED,
        )

    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> UserModel | bool:
        _user = await UserDao(session).get_by_email(email)
        if not _user or not UtilsService.verify_password(password, _user.password_hash):
            return False
        return _user

    @staticmethod
    async def user_email_exists(session: AsyncSession, email: str) -> UserModel | None:
        return await UserDao(session).get_by_email(email)

    @staticmethod
    async def login(form_data: OAuth2PasswordRequestForm, session: AsyncSession) -> Token:
        _user = await UserService.authenticate_user(session, form_data.username, form_data.password)
        if not _user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password",
            )
        print(_user)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = UtilsService.create_access_token(data={"sub": _user.email, "user_id": _user.id}, expires_delta=access_token_expires)
        return Token(access_token=access_token, token_type="Bearer")
    
    @staticmethod
    async def get_user_role(user_id: int, session: AsyncSession) -> dict:
        """
        Получение роли пользователя.
        """
        dao = UserDao(session)
        user = await dao.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return {"email": user.email, "role": user.role}

    @staticmethod
    async def get_current_user(
        session: AsyncSession = Depends(get_session),
        token: str = Depends(oauth2_scheme),
    ) -> UserModel:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if not email:
                raise credentials_exception
            token_data = TokenData(email=email)
        except JWTError:
            raise credentials_exception

        _user = await UserDao(session).get_by_email(email=token_data.email)
        if not _user:
            raise credentials_exception
        return _user

    @staticmethod
    async def get_all_users(session: AsyncSession) -> list[UserOut]:
        all_users = await UserDao(session).get_all()
        return [UserOut.model_validate(_user) for _user in all_users]

    @staticmethod
    async def delete_all_users(session: AsyncSession):
        await UserDao(session).delete_all()
        return JSONResponse(
            content={"message": "All users deleted successfully!"},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    async def change_password(
        password_data: ChangePasswordIn,
        current_user: UserModel,
        session: AsyncSession = Depends(get_session),
    ):
        if not UtilsService.verify_password(password_data.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password!",
            )
        current_user.password_hash = UtilsService.get_password_hash(password_data.new_password)
        session.add(current_user)
        await session.commit()
        return JSONResponse(
            content={"message": "Password updated successfully!"},
            status_code=status.HTTP_200_OK,
        )

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession) -> UserOut:
        _user = await UserDao(session).get_by_id(user_id)
        if not _user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with the given id does not exist!",
            )
        return UserOut.model_validate(_user)

    @staticmethod
    async def delete_user_by_id(user_id: int, session: AsyncSession):
        _user = await UserDao(session).delete_by_id(user_id)
        if not _user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User with the given id does not exist!",
            )
        return JSONResponse(
            content={"message": "User deleted successfully!"},
            status_code=status.HTTP_200_OK,
        )
    
    @staticmethod
    async def update_user_role(user_id: int, new_role: str, session: AsyncSession):
        dao = UserDao(session)
        updated_user = await dao.update_role(user_id, new_role)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return {"message": f"User role updated to {new_role}", "user": updated_user.email, "new_role": updated_user.role}


CurrentUserDep = Annotated[UserModel, Depends(UserService.get_current_user)]
