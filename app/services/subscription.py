from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.daos.subscription import SubscriptionDao
from app.schemas.subscription import SubscriptionIn, SubscriptionOut
from datetime import timedelta, datetime

MONTHLY_PLAN_ID = "price_1QYvQSFsQfGGW0IC3wOIIJOD" 

class SubscriptionService:
    @staticmethod
    async def create_subscription(subscription_data: SubscriptionIn, session: AsyncSession) -> SubscriptionOut:
        dao = SubscriptionDao(session)
        new_subscription = await dao.create(subscription_data.model_dump())
        return SubscriptionOut.model_validate(new_subscription)

    @staticmethod
    async def get_subscription_by_id(subscription_id: int, session: AsyncSession) -> SubscriptionOut:
        dao = SubscriptionDao(session)
        subscription = await dao.get_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found!",
            )
        return SubscriptionOut.model_validate(subscription)

    @staticmethod
    async def get_user_subscriptions(user_id: int, session: AsyncSession) -> list[SubscriptionOut]:
        dao = SubscriptionDao(session)
        subscriptions = await dao.get_by_user_id(user_id)
        return [SubscriptionOut.model_validate(sub) for sub in subscriptions]

    @staticmethod
    async def delete_subscription_by_id(subscription_id: int, session: AsyncSession):
        dao = SubscriptionDao(session)
        subscription = await dao.get_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found!",
            )
        await dao.delete_by_id(subscription_id)
        return {"message": "Subscription deleted successfully!"}
    
    @staticmethod
    async def handle_successful_payment(user_id: int, price_id: str, session: AsyncSession):
        """Создание подписки после успешной оплаты."""
        # Определяем дату начала и окончания подписки
        start_date = datetime.utcnow()
        duration = 30 if price_id == MONTHLY_PLAN_ID else 365
        end_date = start_date + timedelta(days=duration)

        subscription_data = {
            "user_id": user_id,
            "plan_id": price_id,
            "start_date": start_date,
            "end_date": end_date,
        }

        await SubscriptionDao(session).create(subscription_data)

    @staticmethod
    async def handle_payment_failure(event_data: dict, session: AsyncSession):
        """Обработка отказа в оплате"""
        subscription_id = event_data["id"]
        subscription = await SubscriptionDao(session).get_by_id(subscription_id)
        if subscription:
            subscription.status = "failed"
            session.add(subscription)
            await session.commit()

    @staticmethod
    async def handle_subscription_cancellation(event_data: dict, session: AsyncSession):
        """Обработка отмены подписки"""
        subscription_id = event_data["id"]
        subscription = await SubscriptionDao(session).get_by_id(subscription_id)
        if subscription:
            subscription.status = "canceled"
            session.add(subscription)
            await session.commit()

    @staticmethod
    async def handle_subscription_update(event_data: dict, session: AsyncSession):
        """Обновление данных подписки"""
        subscription_id = event_data["id"]
        subscription = await SubscriptionDao(session).get_by_id(subscription_id)
        if subscription:
            subscription.plan = event_data["items"]["data"][0]["price"]["id"]
            subscription.end_date = datetime.fromtimestamp(event_data["current_period_end"])
            session.add(subscription)
            await session.commit()