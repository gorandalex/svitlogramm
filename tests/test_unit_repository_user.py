import unittest
from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from svitlogram.database.models import User, UserRole
from svitlogram.schemas.user import UserCreate, ProfileUpdate
from svitlogram.repository.users import (
    create_user,
    get_user_by_email,
    get_user_by_email_or_username,
    get_user_by_username,
    get_user_by_id,
    update_token,
    update_avatar,
    update_password,
    update_email,
    confirmed_email,
    update_user_profile,
    user_update_role,
    user_update_is_active,
)


class TestRepositoryUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.body = UserCreate(
            username="username",
            email="email@example.com",
            password="qwerty_123",
            first_name="Test",
            last_name="User"
        )
        self.update = ProfileUpdate(
            username="Patric",
            first_name="Patrick",
            last_name="Pink"
        )

    async def test_create_user(self):

        result = await create_user(self.body, self.session)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, self.body.username)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.password, self.body.password)
        self.assertTrue(hasattr(result, 'id'))

        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    async def test_confirmed_email(self):
        user = User(id=1)

        result = await confirmed_email(user, self.session)

        self.assertIsNone(result)
        self.assertTrue(user.email_verified)
        self.session.commit.assert_called_once()

    async def test_get_user_by_id_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await get_user_by_id(user_id=1, db=self.session)

        self.assertEqual(result, mock_user)

    async def test_get_user_by_id_not_found(self):
        self.session.scalar.return_value = None

        result = await get_user_by_id(user_id=1, db=self.session)

        self.assertIsNone(result)

    async def test_get_user_by_email_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await get_user_by_email(email="email@example.com", db=self.session)

        self.assertEqual(result, mock_user)

    async def test_get_user_by_email_not_found(self):
        self.session.scalar.return_value = None

        result = await get_user_by_email(email="email@example.com", db=self.session)

        self.assertIsNone(result)

    async def test_update_token_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        new_token = "new_token"
        result = await update_token(user=mock_user, token=new_token, db=self.session)

        self.assertIsNone(result)
        self.assertEqual(mock_user.refresh_token, new_token)
        self.session.commit.assert_called_once()

    async def test_update_avatar_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await update_avatar(user_id=1, url="new_avatar_url", db=self.session)

        self.assertEqual(result, mock_user)
        self.session.commit.assert_called_once()

    async def test_update_email_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await update_email(user_id=1, email="email@example.com", db=self.session)

        self.assertEqual(result, mock_user)
        self.session.commit.assert_called_once()

    async def test_update_password_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await update_password(user_id=1, password="new_password", db=self.session)

        self.assertEqual(result, mock_user)
        self.session.commit.assert_called_once()

    async def test_get_user_by_email_or_username_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await get_user_by_email_or_username(email="email@example.com", username="username", db=self.session)

        self.assertEqual(result, mock_user)

    async def test_get_user_by_email_or_username_not_found(self):
        self.session.scalar.return_value = None

        result = await get_user_by_email_or_username(email="email@example.com", username="username", db=self.session)

        self.assertIsNone(result)

    async def test_get_user_by_username_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await get_user_by_username(username="username", db=self.session)

        self.assertEqual(result, mock_user)

    async def test_get_user_by_username_not_found(self):
        self.session.scalar.return_value = None

        result = await get_user_by_username(username="username", db=self.session)

        self.assertIsNone(result)

    async def test_user_update_role_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await user_update_role(user=mock_user, role=UserRole.moderator, db=self.session)

        self.assertEqual(result, mock_user)
        self.session.commit.assert_called_once()

    async def test_user_update_is_active_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await user_update_is_active(user=mock_user, is_active=True, db=self.session)

        self.assertEqual(result, mock_user)
        self.session.commit.assert_called_once()

    async def test_update_user_profile_found(self):
        mock_user = User()
        self.session.scalar.return_value = mock_user

        result = await update_user_profile(user_id=1, body=self.update, db=self.session)

        self.assertEqual(result, mock_user)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
