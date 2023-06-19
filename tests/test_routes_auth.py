import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from collections import namedtuple

import pytest
from fastapi_limiter import FastAPILimiter
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from svitlogram.database.models import User, UserRole
from svitlogram.services.auth import AuthService


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


def test_signup(client, user, session, monkeypatch):
    url_path = "/api/auth/signup"
    mock_send_email = MagicMock()
    monkeypatch.setattr('svitlogram.services.email.send_email_confirmed', mock_send_email)

    response = client.post(url_path, json=user)

    user['id'] = response.json()['user']['id']

    assert response.status_code == 201
    assert response.json()["user"]["role"] == UserRole.admin
    assert response.json()["user"]["email"] == user["email"]
    assert response.json()["detail"] == "User successfully created"

    monkeypatch.setattr('svitlogram.services.email.send_email_confirmed', mock_send_email)
    # Test a user creation request with an already existing email
    user = user.copy()
    user['username'] = "test_user2"
    user['password'] = "test_pwd2"

    response = client.post(url_path, json=user)

    assert response.status_code == 409
    assert response.json()["detail"] == "An account with the same email address or username already exists"


def test_login(client, session, user):
    bad_user = {"username": "test_user2",
                "email": "test_user2@gmail.com",
                "password": "123456789",
                'first_name': 'first_name2',
                'last_name': 'last_name2'}
    # Invalid email
    response = client.post(
        "/api/auth/login",
        data={"username": bad_user.get('email'), "password": bad_user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

    # Email not confirmed
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"

    try:
        current_user = session.scalar(
            update(User)
            .values(email_verified=True)
            .filter(User.id == current_user.id)
            .returning(User)
        )
        session.commit()
    except IntegrityError as e:
        return

    session.refresh(current_user)

    # Invalid password
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": bad_user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"

    # Valid data
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_refresh_token_valid_credentials(client, user, token, monkeypatch):
    USER = namedtuple('USER', ['email', 'refresh_token'])

    mock_decode_refresh_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=USER(email=user.get('email'), refresh_token='valid_token'))
    mock_create_access_token = AsyncMock(return_value="new_access_token")
    mock_create_refresh_token = AsyncMock(return_value="new_refresh_token")
    mock_update_token = AsyncMock()

    monkeypatch.setattr("svitlogram.services.auth.AuthService.decode_refresh_token", mock_decode_refresh_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.create_access_token", mock_create_access_token)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.create_refresh_token", mock_create_refresh_token)
    monkeypatch.setattr("svitlogram.repository.users.update_token", mock_update_token)
    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": "Bearer valid_token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["access_token"] == "new_access_token"
    assert data["refresh_token"] == "new_refresh_token"
    assert data["token_type"] == "bearer"
    assert mock_decode_refresh_token.called
    assert mock_get_user_by_email.called
    assert mock_create_access_token.called
    assert mock_create_refresh_token.called
    assert mock_update_token.called


def test_refresh_token_invalid_credentials(client, user, token, monkeypatch):
    USER = namedtuple('USER', ['email', 'refresh_token'])
    mock_decode_refresh_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=USER(email=user.get('email'), refresh_token='valid_token'))
    mock_update_token = AsyncMock()

    monkeypatch.setattr("svitlogram.services.auth.AuthService.decode_refresh_token", mock_decode_refresh_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr("svitlogram.repository.users.update_token", mock_update_token)

    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid refresh token"
    assert mock_decode_refresh_token.called
    assert mock_get_user_by_email.called


def test_confirmed_email_is_confirmed(client, token, user):
    token_email = asyncio.run(AuthService.create_email_token({"sub": user.get('email')}))
    response = client.get(
        f"/api/auth/confirmed_email/{token_email}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


def test_confirmed_email_success(client, session, token, user):
    token_email = asyncio.run(AuthService.create_email_token({"sub": user.get('email')}))
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.email_verified = False
    session.commit()
    response = client.get(
        f"/api/auth/confirmed_email/{token_email}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"


def test_confirmed_email_wrong_user(client, user, monkeypatch):
    token_email = "token_email"
    token = "token"
    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=None)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    response = client.get(
        f"/api/auth/confirmed_email/{token_email}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error"


def test_logout(client, token, user):
    response = client.get('api/auth/logout',
                          headers={"Authorization": f"Bearer {token}"}
                          )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["message"] == "Successful exit"


def test_new_password_success(client, user):
    password = "new_password"
    token = "test_token"

    with patch("svitlogram.services.auth.AuthService.get_email_from_token") as mock_get_email:
        mock_get_email.return_value = user.get('email')

        with patch("svitlogram.services.auth.AuthService.add_token_to_blacklist") as mock_add_token:
            response = client.post(
                f"/api/auth/reset_password/{token}",
                data={"password": password}
            )

            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

            mock_get_email.assert_called_once_with(token)


def test_new_password_wrong_email(client, user):
    password = "new_password"
    token = "test_token"

    with patch("svitlogram.services.auth.AuthService.get_email_from_token") as mock_get_email:
        mock_get_email.return_value = "wrong_email@gmail.com"

        with patch("svitlogram.services.auth.AuthService.add_token_to_blacklist") as mock_add_token:
            response = client.post(
                f"/api/auth/reset_password/{token}",
                data={"password": password}
            )

            assert response.status_code == 400
            assert response.json() == {"detail": "Verification error"}

            mock_get_email.assert_called_once_with(token)


def test_new_password_email_not_verified(client, user):
    USER = namedtuple('USER', ['email_verified'])
    password = "new_password"

    with patch("svitlogram.services.auth.AuthService.get_email_from_token") as mock_get_email:
        mock_get_email.return_value = "test@example.com"

        with patch("svitlogram.repository.users.get_user_by_email") as mock_get_user:
            mock_get_user.return_value = USER(email_verified=False)

            with patch("svitlogram.services.auth.AuthService.add_token_to_blacklist") as mock_add_token:
                response = client.post(
                    f"/api/auth/reset_password/{token}",
                    data={"password": password}
                )

                assert response.status_code == 401
                assert response.json() == {"detail": "Email not confirmed"}


# def test_reset_password(client, token, user, session):
#     # Prepare test data
#     email = user.get('email')
#     body = {"email": email}
#
#     # Send request to the endpoint
#     response = client.post("api/auth/reset_password", json=body)
#
#     # Check the response status code and content
#     assert response.status_code == 200
#     data = response.json()
#     assert data["message"] == "Password reset email sent"
#     assert data["timeout_link"]["seconds"] == 86400  # 24 hours in seconds


def test_reset_password_template_success(client, user, monkeypatch):
    USER = namedtuple('USER', ['email_verified'])
    token = "test_token"
    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=USER(email_verified=True))
    mock_token_is_blacklist = AsyncMock(return_value=False)

    monkeypatch.setattr("svitlogram.services.auth.AuthService.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.token_is_blacklist", mock_token_is_blacklist)

    response = client.get(f"/api/auth/reset_password/{token}")

    assert response.status_code == 200
    assert response.template.name == "new_password.html"


def test_reset_password_template_token_is_blacklist(client, user, monkeypatch):
    USER = namedtuple('USER', ['email_verified'])
    token = "test_token"
    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=USER(email_verified=True))
    mock_token_is_blacklist = AsyncMock(return_value=True)

    monkeypatch.setattr("svitlogram.services.auth.AuthService.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.token_is_blacklist", mock_token_is_blacklist)

    response = client.get(f"/api/auth/reset_password/{token}")

    assert response.status_code == 400
    assert response.json() == {"detail": "The link is no longer active"}


def test_reset_password_template_user_not_found(client, user, monkeypatch):
    token = "test_token"
    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=None)
    mock_token_is_blacklist = AsyncMock(return_value=False)

    monkeypatch.setattr("svitlogram.services.auth.AuthService.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.token_is_blacklist", mock_token_is_blacklist)

    response = client.get(f"/api/auth/reset_password/{token}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Verification error"}


def test_reset_password_template_not_email_verified(client, user, monkeypatch):
    USER = namedtuple('USER', ['email_verified'])
    token = "test_token"
    mock_get_email_from_token = AsyncMock(return_value=user.get('email'))
    mock_get_user_by_email = AsyncMock(return_value=USER(email_verified=False))
    mock_token_is_blacklist = AsyncMock(return_value=False)

    monkeypatch.setattr("svitlogram.services.auth.AuthService.get_email_from_token", mock_get_email_from_token)
    monkeypatch.setattr("svitlogram.repository.users.get_user_by_email", mock_get_user_by_email)
    monkeypatch.setattr("svitlogram.services.auth.AuthService.token_is_blacklist", mock_token_is_blacklist)

    response = client.get(f"/api/auth/reset_password/{token}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Email not confirmed"}


