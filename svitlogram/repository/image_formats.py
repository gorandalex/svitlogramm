from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from svitlogram.database.models import ImageFormat, Image


async def create_image_format(user_id: int, image_id: int, format_: dict, db: AsyncSession) -> Optional[ImageFormat]:
    """
    The create_image_format function creates a new image format in the database.

    :param user_id: int: Identify the user that is creating the image format
    :param image_id: int: Specify the image that the format is for
    :param format_: dict: Pass the format of the image
    :param db: AsyncSession: Pass the database session to the function
    :return: An imageformat object
    """
    try:
        format_ = ImageFormat(
            format=format_,
            user_id=user_id,
            image_id=image_id,
        )
        db.add(format_)

        await db.commit()

        await db.refresh(format_)

        return format_
    except IntegrityError:
        return


async def get_image_formats_by_image_id(user_id: int, image_id: int, db: AsyncSession) -> list[Image]:
    """
    The get_image_formats_by_image_id function returns a list of ImageFormat objects that are associated with the
    image_id parameter. The user_id parameter is used to ensure that only images belonging to the user are returned.

    :param user_id: int: Identify the user
    :param image_id: int: Filter the images by image_id
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of image format objects
    """
    images = await db.scalars(
        select(ImageFormat)
        .filter(ImageFormat.image_id == image_id, ImageFormat.user_id == user_id)
    )

    return images.all()  # noqa


async def get_image_format_by_id(image_format_id: int, db: AsyncSession) -> Image:
    """
    The get_image_format_by_id function returns an ImageFormat object from the database.

    :param image_format_id: int: Specify the image format id
    :param db: AsyncSession: Pass in the database session
    :return: An image object
    """
    return await db.scalar(
        select(ImageFormat)
        .filter(ImageFormat.id == image_format_id)
    )


async def remove_image_format(image_format: ImageFormat, db: AsyncSession) -> None:
    """
    The remove_image_format function removes an image format from the database.

    :param image_format: ImageFormat: Specify what image format we want to delete
    :param db: AsyncSession: Pass the database connection to the function
    :return: None
    """
    await db.delete(image_format)
    await db.commit()
