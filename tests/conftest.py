import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DatabaseError

from main import app
from svitlogram.database.models.base import Base
from svitlogram.database.connect import get_db
from config import settings

DATABASE_URL = settings.DATABASE_URL_TEST


engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    except DatabaseError:  # noqa
        db.rollback()
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture(scope="module")
def user():
    return {"username": "test_user",
            "email": "test_user@gmail.com",
            "password": "12345678",
            'first_name': 'first_name',
            'last_name': 'last_name'}
