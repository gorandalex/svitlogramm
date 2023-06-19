import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from svitlogram.repository.tags import (
    get_tags,
    get_tags_by_list_values,
    get_tag_by_id,
    get_or_create_tags,
    update_tag,
    remove_tag,
    get_list_tags
)
from svitlogram.database.models import Tag
from svitlogram.schemas.tag import TagBase

class TestTags(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_tags(self):
        expected = [Tag(name="some")]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = expected

        self.session.scalars.return_value = mock_scalars

        tags = await get_tags(0, 10, self.session)
        self.assertEqual(expected, tags)

    async def test_get_tags_by_list_values(self):
        expected = [Tag(name="some")]

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = expected

        self.session.scalars.return_value = mock_scalars

        tags = await get_tags_by_list_values(["some"], self.session)
        self.assertEqual(expected, tags)

    async def test_get_tag_by_id(self):
        expected = Tag(id=42, name="some")

        self.session.scalar.return_value = expected

        tags = await get_tag_by_id(42, self.session)
        self.assertEqual(expected, tags)

    async def test_get_or_create_tags(self):
        tag1 = Tag(name="some1")
        tag2 = Tag(name="some2")

        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [tag1]
        self.session.scalars.return_value = mock_scalars

        tags = await get_or_create_tags(["some1", "some2"], self.session)
        self.assertEqual([tag1.name, tag2.name], [tag.name for tag in tags])

    async def test_update_tag(self):
        tag = Tag(id=42, name="some")

        self.session.scalar.return_value = tag

        updated_tag = await update_tag(42, TagBase(name="newname"), self.session)
        self.assertEqual("newname", updated_tag.name)

    async def test_remove_tag(self):
        tag = Tag(id=42, name="some")
        self.session.scalar.return_value = tag
        await remove_tag(42, self.session)
        self.session.delete.assert_called_once_with(tag)

    async def test_get_list_tags(self):
        tags = get_list_tags(["tag1,tag2"])
        self.assertEquals(list({"tag1", "tag2"}), tags)