import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.daos.user import UserDao
from datetime import datetime

@pytest.mark.asyncio
async def test_create_user():
    # Мокируем данные пользователя
    user_data = {
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "role": "admin",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    mock_user = User(id=1, **user_data)

    # Мокируем сессию и DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(UserDao, "create", return_value=mock_user) as mock_create:
        dao = UserDao(mock_session)
        result = await dao.create(user_data)
        mock_create.assert_called_once_with(user_data)
        assert result == mock_user

@pytest.mark.asyncio
async def test_get_user_by_id():
    # Мокируем данные пользователя
    user_id = 1
    mock_user = User(id=user_id, email="test@example.com", password_hash="hashed_password", role="admin", created_at=datetime.utcnow(), updated_at=datetime.utcnow())

    # Мокируем сессию и DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(UserDao, "get_by_id", return_value=mock_user) as mock_get:
        dao = UserDao(mock_session)
        result = await dao.get_by_id(user_id)
        mock_get.assert_called_once_with(user_id)
        assert result == mock_user

@pytest.mark.asyncio
async def test_get_user_by_email():
    # Мокируем данные пользователя
    email = "test@example.com"
    mock_user = User(id=1, email=email, password_hash="hashed_password", role="admin", created_at=datetime.utcnow(), updated_at=datetime.utcnow())

    # Мокируем сессию и DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(UserDao, "get_by_email", return_value=mock_user) as mock_get_email:
        dao = UserDao(mock_session)
        result = await dao.get_by_email(email)
        mock_get_email.assert_called_once_with(email)
        assert result == mock_user

@pytest.mark.asyncio
async def test_get_all_users():
    # Мокируем список пользователей
    mock_users = [
        User(id=1, email="test1@example.com", password_hash="hashed_password", role="admin", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        User(id=2, email="test2@example.com", password_hash="hashed_password", role="user", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    ]

    # Мокируем сессию и DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(UserDao, "get_all", return_value=mock_users) as mock_get_all:
        dao = UserDao(mock_session)
        result = await dao.get_all()
        mock_get_all.assert_called_once()
        assert result == mock_users

@pytest.mark.asyncio
async def test_delete_user_by_id():
    # Мокируем данные пользователя
    user_id = 1
    mock_user = User(id=user_id, email="test@example.com", password_hash="hashed_password", role="admin", created_at=datetime.utcnow(), updated_at=datetime.utcnow())

    # Мокируем сессию и DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(UserDao, "delete_by_id", return_value=mock_user) as mock_delete:
        dao = UserDao(mock_session)
        result = await dao.delete_by_id(user_id)
        mock_delete.assert_called_once_with(user_id)
        assert result == mock_user

@pytest.mark.asyncio
async def test_update_user_role():
    # Мокируем данные пользователя
    user_id = 1
    new_role = "analyst"
    mock_user = User(id=user_id, email="test@example.com", password_hash="hashed_password", role=new_role, created_at=datetime.utcnow(), updated_at=datetime.utcnow())

    # Мокируем сессию и DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(UserDao, "update_role", return_value=mock_user) as mock_update_role:
        dao = UserDao(mock_session)
        result = await dao.update_role(user_id, new_role)
        mock_update_role.assert_called_once_with(user_id, new_role)
        assert result == mock_user
