import unittest
from unittest.mock import MagicMock
from svitlogram.database.models import ImageFormat, User, Image
from svitlogram.repository.image_formats import create_image_format, get_image_formats_by_image_id
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


class TestRepositoryImagesFormats(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.user = User(id=1)
        self.image = Image(id=1)
        self.body = {
            "width": 0,
            "height": 0,
            "crop": "fill",
            "gravity": "center"
        }

    async def test_create_image_format_success(self):

        result = await create_image_format(user_id=self.user.id, image_id=self.image.id, format_=self.body, db=self.session)

        self.assertIsInstance(result, ImageFormat)
        self.assertEqual(result.format, self.body)
        self.assertEqual(result.user_id, self.user.id)
        self.assertEqual(result.image_id, self.image.id)
        self.assertTrue(hasattr(result, 'id'))

        self.session.add.assert_called_once_with(result)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(result)

    async def test_create_image_format_failure(self):

        self.session.commit.side_effect = IntegrityError(None, None, None)

        result = await create_image_format(user_id=self.user.id, image_id=self.image.id, format_=self.body, db=self.session)

        self.assertIsNone(result)

    async def test_get_image_formats_by_image_id(self):

        image_formats = [
            ImageFormat(user_id=self.user.id, image_id=self.image.id),
            ImageFormat(user_id=self.user.id, image_id=self.image.id),
            ImageFormat(user_id=self.user.id, image_id=self.image.id)
        ]

        self.session.scalars.return_value.all.return_value = image_formats

        result = await get_image_formats_by_image_id(user_id=self.user.id, image_id=self.image.id, db=self.session)

        self.assertTrue(result)
        self.assertEqual(await result, image_formats)

    async def test_get_image_formats_by_image_id_not_found(self):

        self.session.scalars.return_value.all.return_value = None

        result = await get_image_formats_by_image_id(user_id=self.user.id, image_id=self.image.id, db=self.session)

        self.assertIsNone(await result)


if __name__ == '__main__':
    unittest.main()
