from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session

from svitlogram.database.models.image_raiting import ImageRating
from svitlogram.database.models.images import Image
from svitlogram.repository.images import get_image_by_id


async def create_rating(user_id: int, rating: int, image_id: int, db: Session) -> ImageRating:
    """
    The create function creates a new ImageRating object and adds it to the database.

    :param user_id: int: Specify the user_id of the rating
    :param rating: int: Create a new rating object
    :param image_id: int: Specify the image_id of the rating
    :param db: Session: Pass the database session to the function
    :return: The new rating object
    """
    rating = ImageRating(rating=rating, image_id=image_id, user_id=user_id)

    db.add(rating)
    db.commit()
    db.refresh(rating)

    image = await get_image_by_id(image_id=image_id, db=db)
    image.avg_rating = round(await get_image_rating(image, db=db), 1)
    db.commit()
    db.refresh(image)
    
    return rating


async def get_all_image_ratings(image_id: int, db: Session) -> list[ImageRating]:
    """
    The get_all_ratings function returns all ratings for a given image.

    :param image_id: int: Specify the image_id of the image we want to get all ratings for
    :param db: Session: Pass in the database session
    :return: A list of dictionaries
    """
    ratings = db.scalars(
        select(ImageRating)
        .filter(ImageRating.image_id == image_id)
    )

    return ratings.all()  # noqa


async def get_rating_by_id(rating_id: int, db: Session) -> Optional[ImageRating]:
    """
    The get_rating_by_id function takes in a rating_id and an AsyncSession object.
    It then queries the database for the ImageRating with that id, and returns it.

    :param rating_id: int: Specify the id of the rating that is being queried
    :param db: Session: Pass the database connection to the function
    :return: A rating object from the database
    """
    return db.scalar(
        select(ImageRating)
        .filter(ImageRating.id == rating_id)
    )


async def get_rating_by_image_id_and_user(user_id: int, image_id: int, db: Session) -> Optional[ImageRating]:
    """
    The get_rating_by_user_id_and_image_id function returns the rating of an image by a user.

    :param user_id: int: Specify the user_id of the image rating
    :param image_id: int: Filter the query by image_id
    :param db: Session: Pass in the database session
    :return: The rating of the user for the image with id = image_id
    """
    return db.scalar(
        select(ImageRating)
        .filter(and_(ImageRating.image_id == image_id, ImageRating.user_id == user_id))
    )


async def remove_rating(rating: ImageRating, db: Session) -> None:
    """
    The remove_rating function removes a rating from the database.

    :param rating: ImageRating: Pass in the rating object that we want to remove
    :param db: Session: Pass the database session to the function
    :return: None
    """
    
    image = await get_image_by_id(image_id=rating.image_id, db=db)
    
    db.delete(rating)
    db.commit()

    image.avg_rating = round(await get_image_rating(image, db=db), 1)
    db.commit()
    db.refresh(image)


async def update_rating(rating: ImageRating, new_rating: int, db: Session) -> ImageRating:
    """
    The update_rating function updates the rating of an image.

    :param rating: ImageRating: Pass in the rating object that we want to update
    :param new_rating: int: Pass in the new rating value
    :param db: Session: Pass the database session to the function
    :return: The new rating
    """
    rating.rating = new_rating
    db.commit()

    db.refresh(rating)

    image = await get_image_by_id(image_id=rating.image_id, db=db)
    image.avg_rating = round(await get_image_rating(image, db=db), 1)
    db.commit()
    db.refresh(image)

    return rating

async def get_image_rating(image: Image, db: Session) -> float:
    average_rating = (
        db.query(func.coalesce(func.avg(ImageRating.rating), 0))
        .filter(ImageRating.image_id == image.id)
        .scalar()
    )

    return average_rating    