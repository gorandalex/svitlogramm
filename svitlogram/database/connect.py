from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import settings

DATABASE_URL = settings.db_url

engine = create_engine(DATABASE_URL, max_overflow=5)  #  echo=True,

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except DatabaseError as e:
        db.rollback()
    finally:
        db.close()
