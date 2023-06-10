from svitlogram.repository.comments import (
    create_comment,
    get_comments_by_image_or_user_id,
    update_comment,
    remove_comment,
    get_comment_by_id,
)
from svitlogram.database.models import ImageComment
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import MagicMock
import unittest
import sys
import os

# add parent directory of src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestComments(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.comment = dict(data="Some text", image_id=2, user_id=1)

    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.comment_id = 2

    async def test_create_comment(self):
        comment = ImageComment(**self.comment)

        result = await create_comment(user_id=self.comment['user_id'],
                                      image_id=self.comment['image_id'],
                                      data=self.comment['data'],
                                      db=self.session)

        self.assertEqual(result.user_id, comment.user_id)
        self.assertEqual(result.image_id, comment.image_id)
        self.assertEqual(result.data, comment.data)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_comment_by_id(self):
        comment = ImageComment(**self.comment)
        self.session.scalar.return_value = comment

        result = await get_comment_by_id(comment_id=self.comment_id, db=self.session)  # noqa

        self.assertEqual(result, comment)

    async def test_get_comment_by_id_not_found(self):
        self.session.scalar.return_value = None

        result = await get_comment_by_id(comment_id=1, db=self.session)

        self.assertIsNone(result)

    async def test_get_comments_by_image_id(self):
        comments = [
            ImageComment(**self.comment),
            ImageComment(**self.comment),
            ImageComment(**self.comment),
        ]
        self.session.scalars.return_value = comments

        image_id = self.comment['image_id']
        result = await get_comments_by_image_or_user_id(
            user_id=None, image_id=image_id, skip=0, limit=2, db=self.session
        )

        for comment in comments:
            if comment.image_id == image_id:
                self.assertIn(comment, result)

    async def test_get_comments_by_user_id(self):
        comments = [
            ImageComment(**self.comment),
            ImageComment(**self.comment),
            ImageComment(**self.comment),
        ]
        self.session.scalars.return_value = comments

        user_id = self.comment['user_id']
        result = await get_comments_by_image_or_user_id(
            user_id=user_id, image_id=None, skip=0, limit=10, db=self.session
        )

        expected_result = [
            comment for comment in comments if comment.user_id == self.comment['user_id']]
        self.assertEqual(result, expected_result)

    async def test_get_comments_by_image_and_user_id(self):
        comments = [
            ImageComment(**self.comment),
            ImageComment(**self.comment),
            ImageComment(**self.comment),
        ]
        self.session.scalars.return_value = comments

        image_id = self.comment['image_id']
        user_id = self.comment['user_id']
        result = await get_comments_by_image_or_user_id(
            user_id=user_id, image_id=image_id, skip=0, limit=10, db=self.session
        )

        self.assertIn(comments[0], result)
        self.assertIn(comments[1], result)
        self.assertIn(comments[2], result)

    async def test_remove_comment_found(self):
        mock_comment = ImageComment(**self.comment)
        self.session.scalar.return_value = mock_comment

        result = await remove_comment(comment_id=1, db=self.session)

        self.assertEqual(result, mock_comment)

    async def test_remove_comment_not_found(self):
        self.session.scalar.return_value = None

        result = await remove_comment(comment_id=1, db=self.session)

        self.assertIsNone(result)

    async def test_update_comment(self):
        updated_comment_data = "Updated comment"

        mock_comment = ImageComment(id=1, data=updated_comment_data)
        self.session.scalar.return_value = mock_comment
        self.session.commit.return_value = None

        edited_comment = await update_comment(comment_id=mock_comment.id, data=updated_comment_data, db=self.session)

        self.assertIsNotNone(edited_comment)
        self.assertEqual(edited_comment, mock_comment)

    async def test_update_comment__not_found(self):
        self.session.scalar.return_value = None
        self.session.commit.return_value = None

        result = await update_comment(comment_id=1, data=self.comment['data'], db=self.session)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
