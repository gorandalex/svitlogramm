import unittest

from sqlalchemy import func

import svitlogram.repository.tags
from unittest.mock import MagicMock, patch, mock_open
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from svitlogram.database.models import Image, Tag, ImageRating
from svitlogram.repository.images import (
    get_image_by_id,
    create_image, delete_image, update_description, get_images, SortMode,
)
from svitlogram.repository.tags import get_or_create_tags


class TestImages(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Set up the test database session
        self.session = MagicMock(spec=Session)
        self.id = 1
        self.tags = ['tag1', 'tag2']
        self.description = "some text for test"
        self.user_id = 1
        self.public_id = "1"

    async def test_get_image_by_id(self):
        image = Image(id=self.id)
        self.session.scalar.return_value = image
        result = await get_image_by_id(self.id, self.session)

        self.assertEqual(image, result)

    async def test_create_image(self):
        tags = ['tag1', 'tag2']
        image = Image(
            user_id=self.user_id,
            description=self.description,
            public_id=self.public_id,
            tags=[Tag(name='tag1'), Tag(name='tag2')]
        )

        result = await create_image(self.user_id, self.description, tags, self.public_id, self.session)
        if self.tags:
            with patch.object(svitlogram.repository.tags, "get_or_create_tags") as mock_get_or_create_tags:
                mock_get_or_create_tags.return_value = image.tags
                result.tags = await mock_get_or_create_tags(self.tags, self.session)

        self.assertEqual(result.user_id, image.user_id)
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.public_id, image.public_id)
        self.assertEqual(result.tags, image.tags)

    async def test_delete_image(self):
        image = Image()
        self.session.query(Image).filter_by().first.return_value = image

        await delete_image(image, self.session)

        self.session.delete.assert_called_once_with(image)
        self.session.commit.assert_called_once()

    async def test_update_description(self):
        image = Image(
            id=1,
            user_id=self.user_id,
            description=self.description,
            public_id=self.public_id,
            tags=[Tag(name='tag1'), Tag(name='tag2')])
        self.session.scalar.return_value = image

        new_description = "Some text for test_2"
        new_tags = ['tag_nest', 'tag_test']
        with patch.object(svitlogram.repository.tags, "get_or_create_tags") as mock_get_or_create_tags:
            mock_get_or_create_tags.return_value = image.tags
        with patch.object(svitlogram.repository.images, "get_image_by_id") as mock_get_image_by_id:
            mock_get_image_by_id.return_value = image

        result = await update_description(image.id, new_description, new_tags, self.session)

        self.assertEqual(result, image)
        self.assertEqual(result.user_id, image.user_id)

    async def test_get_images(self):
        images = [Image() for _ in range(5)]
        self.session.query(Image).limit().offset().all.return_value = images

        result = await get_images("", "", "", "",)
        self.assertEqual(result, images)





