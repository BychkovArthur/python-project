import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.subscription import SubscriptionService
from app.schemas.subscription import SubscriptionIn, SubscriptionOut
from app.daos.subscription import SubscriptionDao
from datetime import datetime, timedelta

MONTHLY_PLAN_ID = "price_1QYvQSFsQfGGW0IC3wOIIJOD"

@pytest.mark.asyncio
async def test_create_subscription():
    # Мокируем данные
    subscription_data = SubscriptionIn(user_id=1, plan_id=MONTHLY_PLAN_ID)
    mock_subscription = SubscriptionOut(
        id=1, 
        user_id=1, 
        plan_id="monthly", 
        start_date=datetime.utcnow(), 
        end_date=datetime.utcnow() + timedelta(days=30)
    )

    # Мокируем DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(SubscriptionDao, 'create', return_value=mock_subscription) as mock_create:
        result = await SubscriptionService.create_subscription(subscription_data, mock_session)
        mock_create.assert_called_once_with(subscription_data.model_dump())
        assert result == mock_subscription

@pytest.mark.asyncio
async def test_get_subscription_by_id():
    # Мокируем данные
    subscription_id = 1
    mock_subscription = SubscriptionOut(
        id=1, 
        user_id=1, 
        plan_id="monthly", 
        start_date=datetime.utcnow(), 
        end_date=datetime.utcnow() + timedelta(days=30)
    )

    # Мокируем DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(SubscriptionDao, 'get_by_id', return_value=mock_subscription) as mock_get:
        result = await SubscriptionService.get_subscription_by_id(subscription_id, mock_session)
        mock_get.assert_called_once_with(subscription_id)
        assert result == mock_subscription

@pytest.mark.asyncio
async def test_get_user_subscriptions():
    # Мокируем данные
    user_id = 1
    mock_subscriptions = [
        SubscriptionOut(
            id=1, 
            user_id=1, 
            plan_id="monthly", 
            start_date=datetime.utcnow(), 
            end_date=datetime.utcnow() + timedelta(days=30)
        )
    ]

    # Мокируем DAO
    mock_session = AsyncMock(spec=AsyncSession)
    with patch.object(SubscriptionDao, 'get_by_user_id', return_value=mock_subscriptions) as mock_get_user_subs:
        result = await SubscriptionService.get_user_subscriptions(user_id, mock_session)
        mock_get_user_subs.assert_called_once_with(user_id)
        assert result == mock_subscriptions

@pytest.mark.asyncio
async def test_handle_successful_payment():
    # Мокируем данные
    user_id = 1
    price_id = MONTHLY_PLAN_ID
    mock_session = AsyncMock(spec=AsyncSession)

    # Мокируем DAO
    with patch.object(SubscriptionDao, 'create') as mock_create:
        await SubscriptionService.handle_successful_payment(user_id, price_id, mock_session)
        mock_create.assert_called_once()

@pytest.mark.asyncio
async def test_delete_subscription_by_id():
    subscription_id = 1
    mock_session = AsyncMock(spec=AsyncSession)

    # Мокируем DAO
    with patch.object(SubscriptionDao, 'delete_by_id', return_value=None) as mock_delete:
        result = await SubscriptionService.delete_subscription_by_id(subscription_id, mock_session)
        mock_delete.assert_called_once_with(subscription_id)
        assert result == {"message": "Subscription deleted successfully!"}

