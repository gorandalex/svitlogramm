import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from sqlalchemy import select, update, or_, func, RowMapping

from svitlogram.database.models.users import User, UserRole
from svitlogram.schemas.user import UserCreate as UserModel
from svitlogram.repository.users import (
    get_user_by_email,
    get_user_by_email_or_username,
    get_user_by_username,
    get_user_by_id,
    create_user,
    confirmed_email,
    update_token,
    update_avatar,
    update_password,
    update_email,
    update_user_profile,
    user_update_role,
    user_update_is_active,
    get_user_profile_by_username,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = MagicMock(spec=User)
        self.user_test = User(
            id=1,
            username='username',
            email='user1@example.com',
            first_name='first_name',
            last_name='last_name',
            password='password',
            email_verified=False,
            role=UserRole.admin,
        )

    async def test_create_user(self):
        db_mock = self.session
        add_mock = self.session.add
        commit_mock = self.session.commit
        refresh_mock = self.session.refresh
        user_test = self.user_test

        # Create a dummy user payload
        user_payload = User(email='user1@example.com')

        # Call the create_user function
        new_user = await create_user(UserModel(**user_test.__dict__), db_mock)

        # Assert the expected behavior
        self.assertIsInstance(new_user, User)
        self.assertEqual(new_user.username, user_test.username)
        self.assertEqual(new_user.email, user_payload.email)
        self.assertEqual(new_user.email, user_test.email)
        self.assertEqual(new_user.first_name, user_test.first_name)
        self.assertEqual(new_user.username, user_test.username)
        self.assertEqual(new_user.last_name, user_test.last_name)
        self.assertNotEqual(new_user.role, UserRole.admin)
        self.assertEqual(new_user.refresh_token, None)

        self.session.add.assert_called_once_with(new_user)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        add_mock.assert_called_once_with(new_user)
        commit_mock.assert_called_once()
        refresh_mock.assert_called_once()

    async def test_get_user_by_email(self):
        db_mock = self.session

        # Create some dummy user data
        user1 = User(email='user1@example.com')
        user2 = User(email='user2@example.com')
        user3 = User(email='user3@example.com')

        self.session.query().filter().first.return_value = user1
        result = await get_user_by_email('user1@example.com', db_mock)
        self.assertEqual(result, user1)

        # Test case 2: User does not exist in the database
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email('user4@example.com', db_mock)
        self.assertIsNone(result)

    async def test_get_user_by_email_or_username(self):
        db_mock = self.session

        # Create some dummy user data
        user1 = User(email='user1@example.com', username='user1')
        user2 = User(email='user2@example.com', username='user2')
        user3 = User(email='user3@example.com', username='user3')

        self.session.query().filter().first.return_value = user1
        result = await get_user_by_email_or_username('user1@example.com', '', db_mock)
        self.assertEqual(result, user1)

        self.session.query().filter().first.return_value = user1
        result = await get_user_by_email_or_username('', 'user1', db_mock)
        self.assertEqual(result, user1)

        # Test case 3: User does not exist in the database
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email_or_username('user4@example.com', 'user4', db_mock)
        self.assertIsNone(result)

    async def test_get_user_by_username(self):
        db_mock = self.session

        # Create some dummy user data
        user1 = User(email='user1@example.com', username='user1')
        user2 = User(email='user2@example.com', username='user2')
        user3 = User(email='user3@example.com', username='user3')

        self.session.query().filter().first.return_value = user1
        result = await get_user_by_username('user1', db_mock)
        self.assertEqual(result, user1)

        # Test case 2: User does not exist in the database
        self.session.query().filter().first.return_value = None
        result = await get_user_by_username('user4', db_mock)
        self.assertIsNone(result)

    async def test_get_user_by_id(self):
        db_mock = self.session

        # Create some dummy user data
        user1 = User(email='user1@example.com', username='user1')
        user2 = User(email='user2@example.com', username='user2')
        user3 = User(email='user3@example.com', username='user3')

        self.session.query().filter().first.return_value = user1
        result = await get_user_by_id(1, db_mock)
        self.assertEqual(result, user1)

        # Test case 2: User does not exist in the database
        self.session.query().filter().first.return_value = None
        result = await get_user_by_id(4, db_mock)
        self.assertIsNone(result)

    async def test_update_token(self):
        user_test = self.user_test
        token = 'new token'

        self.session.commit = MagicMock()
        await update_token(user_test, token, self.session)

        self.assertEqual(user_test.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        # Create some dummy user data
        user1 = User(email='user1@example.com', username='user1')
        avatar = 'https://example.com/avatar.jpg'

        self.session.query().filter().first.return_value = user1
        await update_avatar(user1.id, avatar, self.session)

        self.assertEqual(user1.avatar, avatar)
        self.session.commit.assert_called_once()

    async def test_update_password(self):
        # Create some dummy user data
        user1 = User(email='user1@example.com', username='user1', password='password')
        password = 'qwerty123'

        self.session.query().filter().first.return_value = user1
        await update_password(user1.id, password, self.session)

        self.assertEqual(user1.password, password)
        self.session.commit.assert_called_once()

    async def test_update_email(self):
        # # Create some dummy user data
        # user1 = User(email='user1@example.com', username='user1', password='password')
        # email = 'user_adimin1@example.com'
        #
        # self.session.scalar(update(User).values().filter().returning).return_value = user1
        # await update_email(user1.id, email, self.session)
        #
        # self.assertEqual(user1.email, email)
        # self.session.commit.assert_called_once()
        ...

    async def test_confirmed_email(self):
        email = 'user1@example.com'

        user_mock = MagicMock(spec=User)
        user_mock.email_verified = True

        self.session.query().filter().one_or_none.return_value = user_mock
        self.session.commit = MagicMock()

        await confirmed_email(user_mock, self.session)

        self.assertTrue(user_mock.email_verified)
        self.session.commit.assert_called_once()

    async def test_user_update_role(self):
        email = 'user1@example.com'

        user_mock = MagicMock(spec=User)
        role = UserRole.admin
        user_mock.role = role

        self.session.query().filter().one_or_none.return_value = user_mock
        self.session.commit = MagicMock()

        await user_update_role(user_mock, UserRole.admin, self.session)

        self.assertEqual(user_mock.role, role)
        self.session.commit.assert_called_once()

    async def test_user_update_is_active(self):
        email = 'user1@example.com'

        user_mock = MagicMock(spec=User)
        user_mock.is_active = True

        self.session.query().filter().one_or_none.return_value = user_mock
        self.session.commit = MagicMock()

        await user_update_is_active(user_mock, True, self.session)

        self.assertTrue(user_mock.is_active)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
