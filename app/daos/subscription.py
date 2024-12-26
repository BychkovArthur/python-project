from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.daos.base import BaseDao
from app.models.subscription import Subscription
from datetime import timedelta, datetime

MONTHLY_PLAN_ID = "price_1QYvQSFsQfGGW0IC3wOIIJOD" 

class SubscriptionDao(BaseDao):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, subscription_data: dict) -> Subscription:
        """Create a new subscription."""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + (timedelta(days=30) if subscription_data["plan_id"] == "monthly" else timedelta(days=365))

            subscription = Subscription(
                user_id=subscription_data["user_id"],
                plan_id="monthly" if subscription_data["plan_id"] == MONTHLY_PLAN_ID else "yearly",
                start_date=start_date,
                end_date=end_date,
            )
            self.session.add(subscription)
            await self.session.commit()
            await self.session.refresh(subscription)
            return subscription
        except Exception as e:
            await self.session.rollback()
            raise ValueError(f"Ошибка при создании подписки: {str(e)}")

    async def get_by_id(self, subscription_id: int) -> Subscription | None:
        """Get a subscription by its ID."""
        statement = select(Subscription).where(Subscription.id == subscription_id)
        return await self.session.scalar(statement)

    async def get_by_user_id(self, user_id: int) -> list[Subscription]:
        """Get all subscriptions for a specific user."""
        statement = select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def delete_by_id(self, subscription_id: int) -> None:
        """Delete a subscription by its ID."""
        await self.session.execute(delete(Subscription).where(Subscription.id == subscription_id))
        await self.session.commit()

    async def delete_all(self):
        pass

    async def get_all(self):
        pass
