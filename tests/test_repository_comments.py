import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session


from svitlogram.database.models import ImageComment
from svitlogram.repository.comments import create_comment, get_comments_by_image_or_user_id, update_comment, remove_comment, get_comment_by_id


class TestComments(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.comment = MagicMock(spec=ImageComment)
        self.comment_test = ImageComment(
            id=1,
            data='some comment',
            image_id=3,
            user_id=2
        )
        self.comment_test2 = ImageComment(
            id=2,
            data='another comment',
            image_id=4,
            user_id=5
        )
        self.comment_test3 = ImageComment(
            id=3,
            data='some another comment',
            image_id=5,
            user_id=6
        )

    def tearDown(self):
        pass

    async def test_create_comment(self):
        comment = self.comment_test

        result = await create_comment(user_id=comment.user_id,
                                      image_id=comment.image_id,
                                      data=comment.data,
                                      db=self.session)

        self.assertEqual(result.user_id, comment.user_id)
        self.assertEqual(result.image_id, comment.image_id)
        self.assertEqual(result.data, comment.data)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_comment_by_id(self):
        comment = self.comment_test
        self.session.scalar.return_value = comment

        result = await get_comment_by_id(comment_id=self.id, db=self.session)  # noqa

        self.assertEqual(result, comment)

    async def test_get_comment_by_id_not_found(self):
        self.session.scalar.return_value = None

        result = await get_comment_by_id(comment_id=5, db=self.session)

        self.assertIsNone(result)

    async def test_remove_comment_found(self):
        comment = self.comment_test
        self.session.scalar.return_value = comment

        result = await remove_comment(comment_id=1, db=self.session)

        self.assertEqual(result, comment)

    async def test_remove_comment_not_found(self):
        self.session.scalar.return_value = None

        result = await remove_comment(comment_id=1, db=self.session)

        self.assertIsNone(result)

    async def test_update_comment(self):
        updated_comment_data = "new comment"

        mock_comment = ImageComment(id=1, data=updated_comment_data)
        self.session.scalar.return_value = mock_comment
        self.session.commit.return_value = None

        updated_comment = await update_comment(comment_id=mock_comment.id, data=updated_comment_data, db=self.session)

        self.assertIsNotNone(updated_comment)
        self.assertEqual(updated_comment, mock_comment)

    async def test_update_comment__not_found(self):
        self.session.scalar.return_value = None
        self.session.commit.return_value = None

        result = await update_comment(comment_id=1, data=self.comment_test.data, db=self.session)

        self.assertIsNone(result)
    async def test_get_comment_by_user_id(self):
        comments = [self.comment_test, self.comment_test2, self.comment_test3]
        user_id = self.comment_test.user_id
        mock_all = MagicMock()
        mock_all.return_value = [comment for comment in comments if comment.user_id == user_id]
        scalars_mock = MagicMock()
        scalars_mock.all = mock_all
        self.session.scalars.return_value = scalars_mock

        result = await get_comments_by_image_or_user_id(
            user_id=user_id,
            image_id=None,
            skip=0,
            limit=10,
            db=self.session
        )

        expected_result = [comment for comment in comments if comment.user_id == user_id]
        self.assertEqual(result, expected_result)

    async def test_get_comments_by_image_id(self):
        comments = [self.comment_test, self.comment_test2, self.comment_test3]
        query_mock = MagicMock()
        query_mock.all.return_value = comments
        self.session.scalars.return_value = query_mock
        image_id = self.comment_test.image_id

        result = await get_comments_by_image_or_user_id(
            user_id=None, image_id=image_id, skip=0, limit=2, db=self.session
        )

        for comment in comments:
            if comment.image_id == image_id:
                self.assertIn(comment, result)


if __name__ == '__main__':
    unittest.main()


