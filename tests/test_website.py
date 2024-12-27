import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.daos.website import WebsiteDao
from app.models.website import Website

@pytest.mark.asyncio
async def test_create_website():
    # Мокируем данные
    website_data = {
        'url': 'https://example.com',
    }
    mock_website = Website(id=1, **website_data)

    # Мокируем сессию
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(WebsiteDao, 'create', return_value=mock_website) as mock_create:
        dao = WebsiteDao(mock_session)
        result = await dao.create(website_data)
        mock_create.assert_called_once_with(website_data)
        assert result == mock_website

@pytest.mark.asyncio
async def test_get_website_by_id():
    # Мокируем данные
    website_id = 1
    mock_website = Website(id=website_id, url="https://example.com")

    # Мокируем сессию
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(WebsiteDao, 'get_by_id', return_value=mock_website) as mock_get:
        dao = WebsiteDao(mock_session)
        result = await dao.get_by_id(website_id)
        mock_get.assert_called_once_with(website_id)
        assert result == mock_website

@pytest.mark.asyncio
async def test_get_website_by_url():
    # Мокируем данные
    mock_website = Website(id=1, url="https://example.com")

    # Мокируем сессию
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(WebsiteDao, 'get_by_url', return_value=mock_website) as mock_get:
        dao = WebsiteDao(mock_session)
        result = await dao.get_by_url("https://example.com")
        mock_get.assert_called_once_with("https://example.com")
        assert result == mock_website

@pytest.mark.asyncio
async def test_get_all_websites():
    # Мокируем данные
    mock_websites = [
        Website(id=1, url="https://example1.com"),
        Website(id=2, url="https://example2.com")
    ]

    # Мокируем сессию
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(WebsiteDao, 'get_all', return_value=mock_websites) as mock_get_all:
        dao = WebsiteDao(mock_session)
        result = await dao.get_all()
        mock_get_all.assert_called_once()
        assert result == mock_websites

@pytest.mark.asyncio
async def test_delete_website_by_id():
    website_id = 1
    mock_website = Website(id=website_id, url="https://example.com")

    # Мокируем сессию
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(WebsiteDao, 'delete_by_id', return_value=mock_website) as mock_delete:
        dao = WebsiteDao(mock_session)
        result = await dao.delete_by_id(website_id)
        mock_delete.assert_called_once_with(website_id)
        assert result == mock_website

@pytest.mark.asyncio
async def test_delete_all_websites():
    # Мокируем сессию
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(WebsiteDao, 'delete_all', return_value=None) as mock_delete_all:
        dao = WebsiteDao(mock_session)
        await dao.delete_all()
        mock_delete_all.assert_called_once()

