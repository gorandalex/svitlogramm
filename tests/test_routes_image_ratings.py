import pytest
from fastapi.testclient import TestClient
from main import app
from svitlogram.database.models import User, ImageRating
from unittest.mock import MagicMock, patch
from fastapi import status


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


def test_create_image_rating(client, token):
    image_id = 1
    rating = 4

    expected = {"image_id": image_id, "rating": rating}
    response = client.post(
        "api/images/ratings/",
        json={"image_id": image_id, "rating": rating},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    actual = response.json()
    assert actual == expected


def test_update_image_rating(client, token):
    image_id = 1
    rating = 4

    expected = {"image_id": image_id, "rating": rating}
    response = client.put(
        "api/images/ratings/",
        json={"image_id": image_id, "rating": rating},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    actual = response.json()
    assert actual == expected


def test_delete_image_rating(client, token):
    rating_id = 1

    expected = {"message": "Rating deleted successfully"}
    response = client.delete(
        f"api/images/ratings/ratings/{rating_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    actual = response.json()
    assert actual == expected


def test_get_all_image_ratings(client, token):
    image_id = 1

    response = client.get(
        f"api/images/ratings/{image_id}/ratings",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
