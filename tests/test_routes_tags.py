import asyncio
from svitlogram.services.auth import AuthService
from unittest.mock import MagicMock
import pytest
from svitlogram.database.models import User, Tag
from sqlalchemy import select

@pytest.fixture()
def token(client, user, session, monkeypatch):
    url_path = "/api/auth/signup"
    mock_send_email = MagicMock()
    monkeypatch.setattr("svitlogram.services.email.send_email_confirmed", mock_send_email)
    client.post(url_path, json=user)

    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.email_verified = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]

def test_create(client, token):
    expected = ["tag1", "tag2", "tag3"]
    response = client.post(
        '/api/tags',
        json=expected,
        headers = {"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    actual = [tag["name"] for tag in data]

    assert type(data) == list
    assert actual == expected

def test_get_tags(client, token):
    expected = ["tag1", "tag2", "tag3"]

    client.post(
        '/api/tags',
        json=expected,
        headers = {"Authorization": f"Bearer {token}"}
    )

    response = client.get(
        '/api/tags',
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()
    actual = [tag["name"] for tag in data]

    assert type(data) == list
    assert actual == expected

def test_get_tag(client, token):
    tags = ["tag1"]

    client.post(
        '/api/tags',
        json=tags,
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get(
        '/api/tags/1',
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()

    assert "tag1" == data["name"]

def test_update_tag(client, token, session):
    tags = ["tag1"]

    client.post(
        '/api/tags',
        json=tags,
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.put(
        '/api/tags',
        json={
            "tag_id": 1,
            "name": "updated_tag"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()

    assert data["name"] == "updated_tag"

    tag = session.scalar(select(Tag).filter(Tag.id == 1))

    assert tag.name == "updated_tag"


def test_delete_tag(client, token, session):
    tags = ["tag1"]

    client.post(
        '/api/tags',
        json=tags,
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.delete(
        '/api/tags/1',
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.json()

    assert data["id"] == 1

    assert None == session.scalar(select(Tag).filter(Tag.id == 1))