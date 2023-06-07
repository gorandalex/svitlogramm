from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import settings


async_engine = create_async_engine(settings.db_url, future=True)

AsyncSessionLocal = sessionmaker(async_engine, autocommit=False, autoflush=False, class_=AsyncSession)  # noqa


# Dependency
async def get_db():
    """
    The get_db function is a context manager that returns the database session.
    It also ensures that the connection to the database is closed after each request.

    :return: A database session
    """
    async with AsyncSessionLocal() as session:
        yield session
