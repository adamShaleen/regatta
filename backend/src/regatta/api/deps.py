from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from regatta.db.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
