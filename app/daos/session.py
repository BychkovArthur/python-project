from sqlalchemy import delete, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

from app.daos.base import BaseDao
from app.models.session import Session


class SessionDao(BaseDao):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, session_data: dict) -> Session:
        """Create a new session."""
        session = Session(**session_data)
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def get_by_id(self, session_id: int) -> Session | None:
        """Get a session by its ID."""
        statement = select(Session).where(Session.id == session_id)
        return await self.session.scalar(statement)

    async def get_all(self) -> list[Session]:
        """Get all sessions, ordered by creation time."""
        statement = select(Session).order_by(Session.created_ts)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_all_descending_by_created_ts(self) -> list[Session]:
        """Get all sessions, ordered by creation time in descending order."""
        statement = select(Session).order_by(desc(Session.created_ts))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def delete_all(self) -> None:
        """Delete all sessions."""
        await self.session.execute(delete(Session))
        await self.session.commit()

    async def delete_by_id(self, session_id: int) -> Session | None:
        """Delete a session by its ID."""
        session = await self.get_by_id(session_id)
        if session:
            statement = delete(Session).where(Session.id == session_id)
            await self.session.execute(statement)
            await self.session.commit()
        return session

    # Additional methods
    async def get_by_prediction_threshold(self, threshold: float) -> list[Session]:
        """Get sessions where prediction is greater than the given threshold."""
        statement = select(Session).where(Session.prediction > threshold)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_payload_websites(self, website_ids: list[int]) -> list[Session]:
        """Get sessions where payload contains websites from the given list."""
        statement = select(Session).where(
            func.jsonb_path_exists(
                Session.payload, f'$.website_id ? (@ in {website_ids})'
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_user_id(self, user_id: int) -> list[Session]:
        """Get sessions by user ID, ordered by creation time."""
        statement = select(Session).where(Session.user_id == user_id).order_by(Session.created_ts)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_website_and_date(self, website_id: int, date: str) -> list[Session]:
        """Get sessions where a website was visited after a specific date."""
        statement = select(Session).where(
            func.jsonb_path_exists(
                Session.payload,
                f'$.?(@.website_id == {website_id} && @.visited_ts > "{date}")'
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_created_after(self, timestamp: str) -> list[Session]:
        """Get sessions created after a specific timestamp."""
        statement = select(Session).where(Session.created_ts > timestamp).order_by(Session.created_ts)
        result = await self.session.execute(statement)
        return result.scalars().all()
