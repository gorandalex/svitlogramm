import json

from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from svitlogram.database.models import ImageFormat, Image


async def create_image_format(user_id: int, image_id: int, format_: dict, db: Session) -> Optional[ImageFormat]:
    """
    The create_image_format function creates a new image format in the database.

    :param user_id: int: Identify the user that is creating the image format
    :param image_id: int: Specify the image that the format is for
    :param format_: dict: Pass the format of the image
    :param db: AsyncSession: Pass the database session to the function
    :return: An imageformat object
    """
    try:
        format_to_base = ImageFormat(
            format=format_,
            user_id=user_id,
            image_id=image_id,
        )
        db.add(format_to_base)

        db.commit()

        db.refresh(format_to_base)

        return format_to_base
    except IntegrityError:
        return


async def get_image_formats_by_image_id(user_id: int, image_id: int, db: Session) -> list[Image]:
    """
    The get_image_formats_by_image_id function returns a list of ImageFormat objects that are associated with the
    image_id parameter. The user_id parameter is used to ensure that only images belonging to the user are returned.

    :param user_id: int: Identify the user
    :param image_id: int: Filter the images by image_id
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of image format objects
    """
    images = db.scalars(
        select(ImageFormat)
        .filter(ImageFormat.image_id == image_id, ImageFormat.user_id == user_id)
    )

    return images.all()  # noqa


async def get_image_format_by_id(image_format_id: int, db: Session) -> Image:
    """
    The get_image_format_by_id function returns an ImageFormat object from the database.

    :param image_format_id: int: Specify the image format id
    :param db: AsyncSession: Pass in the database session
    :return: An image object
    """
    return db.scalar(
        select(ImageFormat)
        .filter(ImageFormat.id == image_format_id)
    )


async def remove_image_format(image_format: ImageFormat, db: Session) -> None:
    """
    The remove_image_format function removes an image format from the database.

    :param image_format: ImageFormat: Specify what image format we want to delete
    :param db: AsyncSession: Pass the database connection to the function
    :return: None
    """
    db.delete(image_format)
    db.commit()
