import unittest

import svitlogram.repository.images
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from svitlogram.database.models import Image, Tag
from svitlogram.repository.images import (
    get_image_by_id,
    create_image,
    get_or_create_tags
)


class TestImages(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Set up the test database session
        self.session = MagicMock(spec=Session)
        self.id = 1
        self.tags = ['tag1', 'tag2']
        self.description = "some text for test"
        self.user_id = 1,
        self.public_id = 1

    # async def test_get_image_by_id(self):
    #     user_id = 1
    #     description = 'Test image'
    #     tags = ['tag1', 'tag2']
    #     public_id = 'public_id'
    #     expected_image = Image(
    #         user_id=user_id,
    #         description=description,
    #         public_id=public_id,
    #         tags=[Tag(name='tag1'), Tag(name='tag2')]
    #     )
    #     self.session.add.return_value = None
    #     self.session.commit.return_value = None
    #     self.session.refresh.return_value = None
    #     get_or_create_tags_mock = MagicMock(return_value=expected_image.tags)
    #
    #     with unittest.mock.patch(
    #             'svitlogram.repository.images.get_or_create_tags', get_or_create_tags_mock
    #     ):
    #         result = await create_image(user_id, description, tags, public_id, self.session)
    #         result.tags = get_or_create_tags_mock
    #
    #     self.assertEqual(result, expected_image)
    #     self.session.add.assert_called_once_with(expected_image)
    #     self.session.commit.assert_called_once()
    #     self.session.refresh.assert_called_once_with(expected_image)
    #     get_or_create_tags_mock.assert_called_once_with(tags, self.session)
