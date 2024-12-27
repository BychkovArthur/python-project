import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.daos.session import SessionDao
from app.models.session import Session
from datetime import datetime, timedelta


@pytest.mark.asyncio
async def test_create_session():
    # Mock session data
    session_data = {
        "user_id": 1,
        "payload": {"website_id": 123, "visited_ts": "2024-12-01T12:34:56"},
        "prediction": 0.95,
        "created_ts": datetime.utcnow()
    }
    mock_session = Session(**session_data, id=1)

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "create", return_value=mock_session) as mock_create:
        dao = SessionDao(mock_db_session)
        result = await dao.create(session_data)
        mock_create.assert_called_once_with(session_data)
        assert result == mock_session


@pytest.mark.asyncio
async def test_get_session_by_id():
    # Mock session
    session_id = 1
    mock_session = Session(id=session_id, user_id=1, payload={}, prediction=0.8, created_ts=datetime.utcnow())

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "get_by_id", return_value=mock_session) as mock_get:
        dao = SessionDao(mock_db_session)
        result = await dao.get_by_id(session_id)
        mock_get.assert_called_once_with(session_id)
        assert result == mock_session


@pytest.mark.asyncio
async def test_get_all_sessions():
    # Mock data
    mock_sessions = [
        Session(id=1, user_id=1, payload={}, prediction=0.8, created_ts=datetime.utcnow()),
        Session(id=2, user_id=1, payload={}, prediction=0.7, created_ts=datetime.utcnow() - timedelta(days=1)),
    ]

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "get_all", return_value=mock_sessions) as mock_get_all:
        dao = SessionDao(mock_db_session)
        result = await dao.get_all()
        mock_get_all.assert_called_once()
        assert result == mock_sessions


@pytest.mark.asyncio
async def test_delete_session_by_id():
    # Mock data
    session_id = 1
    mock_session = Session(id=session_id, user_id=1, payload={}, prediction=0.8, created_ts=datetime.utcnow())

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "delete_by_id", return_value=mock_session) as mock_delete:
        dao = SessionDao(mock_db_session)
        result = await dao.delete_by_id(session_id)
        mock_delete.assert_called_once_with(session_id)
        assert result == mock_session


@pytest.mark.asyncio
async def test_get_by_prediction_threshold():
    # Mock data
    threshold = 0.75
    mock_sessions = [
        Session(id=1, user_id=1, payload={}, prediction=0.8, created_ts=datetime.utcnow()),
        Session(id=2, user_id=2, payload={}, prediction=0.9, created_ts=datetime.utcnow() - timedelta(days=1)),
    ]

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "get_by_prediction_threshold", return_value=mock_sessions) as mock_get:
        dao = SessionDao(mock_db_session)
        result = await dao.get_by_prediction_threshold(threshold)
        mock_get.assert_called_once_with(threshold)
        assert result == mock_sessions


@pytest.mark.asyncio
async def test_get_by_user_id():
    # Mock data
    user_id = 1
    mock_sessions = [
        Session(id=1, user_id=1, payload={}, prediction=0.8, created_ts=datetime.utcnow()),
    ]

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "get_by_user_id", return_value=mock_sessions) as mock_get:
        dao = SessionDao(mock_db_session)
        result = await dao.get_by_user_id(user_id)
        mock_get.assert_called_once_with(user_id)
        assert result == mock_sessions


@pytest.mark.asyncio
async def test_get_by_website_and_date():
    # Mock data
    website_id = 123
    date = "2024-12-01T00:00:00"
    mock_sessions = [
        Session(id=1, user_id=1, payload={}, prediction=0.8, created_ts=datetime.utcnow()),
    ]

    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "get_by_website_and_date", return_value=mock_sessions) as mock_get:
        dao = SessionDao(mock_db_session)
        result = await dao.get_by_website_and_date(website_id, date)
        mock_get.assert_called_once_with(website_id, date)
        assert result == mock_sessions


@pytest.mark.asyncio
async def test_delete_all_sessions():
    # Mock DAO
    mock_db_session = AsyncMock(spec=AsyncSession)
    with patch.object(SessionDao, "delete_all", return_value=None) as mock_delete:
        dao = SessionDao(mock_db_session)
        result = await dao.delete_all()
        mock_delete.assert_called_once()
        assert result is None
