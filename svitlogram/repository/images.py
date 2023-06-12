import enum
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, aliased
from svitlogram.database.models import Image, Tag, ImageRating
from typing import Optional

from .tags import get_or_create_tags

class SortMode(enum.Enum):

    NOT_SORT = 'not_sort'
    RAITING = 'average_rating'
    RAITING_DESC = 'average_rating_desc'
    DATE = 'date_added'
    DATE_DESC = 'date_added_desc'


async def get_image_by_id(image_id: int, db: Session) -> Image:
    """
    The get_image_by_id function returns an image from the database.

    :param image_id: int: Filter the images by id
    :param db: AsyncSession: Pass in the database session to use
    :return: A single image object
    """
    return db.scalar(
        select(Image)
        .filter(Image.id == image_id)
    )


async def create_image(user_id: int, description: str, tags: list[str], public_id: str, db: Session) -> Image:
    """
    The create_image function creates a new image in the database.

    :param user_id: int: Specify the user who uploaded the image
    :param description: str: Describe the image
    :param tags: list[str]: Specify that the tags parameter is a list of strings
    :param public_id: str: Store the public id of the image in cloudinary
    :param db: AsyncSession: Pass in the database session
    :return: An image object
    """
    image = Image(
        user_id=user_id,
        description=description,
        public_id=public_id
    )

    if tags:
        image.tags = await get_or_create_tags(tags, db)

    db.add(image)

    db.commit()

    db.refresh(image)

    return image


async def update_description(image_id: int, description: str, tags: list[str], db: Session) -> Optional[Image]:
    """
    The update_description function updates the description and tags of an image.

    :param image_id: int: Specify the image to update
    :param description: str: Update the description of an image
    :param tags: list[str]: Pass in a list of tags
    :param db: AsyncSession: Pass in the database session
    :return: An image object
    """
    tags = await get_or_create_tags(tags, db)

    image = await get_image_by_id(image_id, db)
    if image:
        image.description = description
        image.tags = tags
        db.commit()
        db.refresh(image)

    return image


async def delete_image(image: Image, db: Session) -> None:
    """
    The delete_image function deletes an image from the database.

    :param image: Image: Pass the image object to be deleted
    :param db: AsyncSession: Pass in the database session
    :return: None, which is the default return value for a function that doesn't explicitly return anything
    """
    db.delete(image)
    db.commit()


async def get_images(
        skip: int,
        limit: int,
        description: str,
        tags: list[str],
        image_id: int,
        user_id: int,
        sort_by: SortMode,
        db: Session
) -> list[Image]:
    """
    The get_images function is used to retrieve images from the database.
    It takes in a skip, limit, description, tags and image_id as parameters.
    The skip parameter is used to determine how many images should be skipped before returning results.
    The limit parameter determines how many results should be returned after skipping the specified number of images.
    If no value for either of these parameters are provided then they default to 0 and 10 respectively (i.e., return all).
    The description parameter allows you to search for an image by its description field using SQL LIKE syntax (e.g., %description% will match any image with

    :param skip: int: Skip the first n images
    :param limit: int: Limit the number of images returned
    :param description: str: Filter the images by description
    :param tags: list[str]: Filter the images by tags
    :param image_id: int: Filter the images by their id
    :param user_id: int: Filter images by user_id
    :param db: AsyncSession: Pass the database connection
    :return: A list of image objects
    """
    query = select(Image)

    if description:
        query = query.filter(Image.description.like(f'%{description}%'))
    if tags:
        for tag in tags:
            query = query.filter(Image.tags.any(Tag.name.ilike(f'%{tag}%')))
    if user_id:
        query = query.filter(Image.user_id == user_id)
    if image_id:
        query = query.filter(Image.id == image_id)
        
    if sort_by == SortMode.RAITING:  # Сортировка по средней оценке
        subquery = (
            db.query(Image.id, func.coalesce(func.avg(ImageRating.rating), 0).label("average_rating"))
            .outerjoin(ImageRating, ImageRating.image_id == Image.id)
            .group_by(Image.id)
            .subquery()
        )
        query = query.join(subquery, Image.id == subquery.c.id).order_by(subquery.c.average_rating.asc())
    elif sort_by == SortMode.RAITING_DESC:  # Сортировка по средней оценке
        subquery = (
            db.query(Image.id, func.coalesce(func.avg(ImageRating.rating), 0).label("average_rating"))
            .outerjoin(ImageRating, ImageRating.image_id == Image.id)
            .group_by(Image.id)
            .subquery()
        )
        query = query.join(subquery, Image.id == subquery.c.id).order_by(subquery.c.average_rating.desc())
    elif sort_by == SortMode.DATE:  # Сортировка по дате добавления
        query = query.order_by(Image.created_at.asc())
    elif sort_by == SortMode.DATE_DESC:  # Сортировка по дате добавления
        query = query.order_by(Image.created_at.desc())

    image = db.scalars(query)

    return image.unique().all()  # noqa
