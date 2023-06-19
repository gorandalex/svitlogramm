import unittest
from unittest.mock import MagicMock, call

from sqlalchemy.orm import Session

from svitlogram.database.models import ImageRating
from svitlogram.repository.image_ratings import (
    create_rating,
    get_all_image_ratings,
    get_rating_by_id,
    get_rating_by_image_id_and_user,
    remove_rating,
    update_rating,
    get_image_rating,
)


class TestImageRatings(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.rating = MagicMock(spec=ImageRating)
        self.rating_test = ImageRating(
            id=1,
            rating=5,
            image_id=3,
            user_id=2
        )
        self.rating_test2 = ImageRating(
            id=2,
            rating=3,
            image_id=4,
            user_id=5
        )

    def tearDown(self):
        pass

    async def test_create_rating(self):
        rating = self.rating_test

        result = await create_rating(user_id=rating.user_id,
                                     rating=rating.rating,
                                     image_id=rating.image_id,
                                     db=self.session)

        self.assertEqual(result.user_id, rating.user_id)
        self.assertEqual(result.image_id, rating.image_id)
        self.assertEqual(result.rating, rating.rating)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_all_image_ratings(self):
        ratings = [self.rating_test, self.rating_test2]
        query_mock = MagicMock()
        query_mock.all.return_value = ratings
        self.session.scalars.return_value = query_mock
        image_id = self.rating_test.image_id
        result = await get_all_image_ratings(image_id=image_id, db=self.session)

        for rating in ratings:
            if rating.image_id == image_id:
                self.assertIn(rating, result)

    async def test_get_rating_by_id(self):
        rating = self.rating_test
        self.session.scalar.return_value = rating

        result = await get_rating_by_id(rating_id=rating.id, db=self.session)

        self.assertEqual(result, rating)

    async def test_get_rating_by_id_not_found(self):
        self.session.scalar.return_value = None

        result = await get_rating_by_id(rating_id=999, db=self.session)

        self.assertIsNone(result)

    async def test_get_rating_by_image_id_and_user(self):
        rating = self.rating_test
        self.session.scalar.return_value = rating

        result = await get_rating_by_image_id_and_user(user_id=rating.user_id,
                                                       image_id=rating.image_id,
                                                       db=self.session)

        self.assertEqual(result, rating)

    async def test_get_rating_by_image_id_and_user_not_found(self):
        self.session.scalar.return_value = None

        result = await get_rating_by_image_id_and_user(user_id=999, image_id=999, db=self.session)

        self.assertIsNone(result)

    async def test_remove_rating(self):
        rating = self.rating_test

        await remove_rating(rating=rating, db=self.session)

        self.session.delete.assert_called_once_with(rating)
        self.assertEqual(self.session.commit.call_count, 2)

    async def test_update_rating(self):
        rating = self.rating_test
        new_rating = 4
        self.session.query().filter().scalar.return_value = 4.5

        result = await update_rating(rating=rating, new_rating=new_rating, db=self.session)

        self.assertEqual(result, rating)
        self.assertEqual(rating.rating, new_rating)

    async def test_get_image_rating(self):
        image = MagicMock()
        average_rating = 4.5
        self.session.query.return_value.filter.return_value.scalar.return_value = average_rating

        result = await get_image_rating(image=image, db=self.session)

        self.assertEqual(result, average_rating)

