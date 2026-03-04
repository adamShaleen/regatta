from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from regatta.config import settings

engine = create_async_engine(settings.database_url, echo=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
