from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.daos.base import BaseDao
from app.models.website import Website


class WebsiteDao(BaseDao):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create(self, website_data: dict) -> Website:
        """Create a new website."""
        website = Website(**website_data)
        self.session.add(website)
        await self.session.commit()
        await self.session.refresh(website)
        return website

    async def get_by_id(self, website_id: int) -> Website | None:
        """Get a website by its ID."""
        statement = select(Website).where(Website.id == website_id)
        return await self.session.scalar(statement)

    async def get_all(self) -> list[Website]:
        """Get all websites."""
        statement = select(Website).order_by(Website.id)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def delete_all(self) -> None:
        """Delete all websites."""
        await self.session.execute(delete(Website))
        await self.session.commit()

    async def delete_by_id(self, website_id: int) -> Website | None:
        """Delete a website by its ID."""
        website = await self.get_by_id(website_id)
        if website:
            statement = delete(Website).where(Website.id == website_id)
            await self.session.execute(statement)
            await self.session.commit()
        return website

    async def get_by_url(self, url: str) -> Website | None:
        """Get a website by its URL."""
        statement = select(Website).where(Website.url == url)
        return await self.session.scalar(statement)
