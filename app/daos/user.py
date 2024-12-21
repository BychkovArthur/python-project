from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.daos.base import BaseDao
from app.models.user import User


class UserDao(BaseDao):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, user_data: dict) -> User:
        """Create a new user."""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by their ID."""
        statement = select(User).where(User.id == user_id)
        return await self.session.scalar(statement)

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by their email."""
        statement = select(User).where(User.email == email)
        return await self.session.scalar(statement)

    async def get_all(self) -> list[User]:
        """Get all users."""
        statement = select(User).order_by(User.id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def delete_all(self) -> None:
        """Delete all users."""
        await self.session.execute(delete(User))
        await self.session.commit()

    async def delete_by_id(self, user_id: int) -> User | None:
        """Delete a user by their ID."""
        user = await self.get_by_id(user_id)
        if user:
            statement = delete(User).where(User.id == user_id)
            await self.session.execute(statement)
            await self.session.commit()
        return user
