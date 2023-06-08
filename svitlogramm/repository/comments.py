from typing import Optional

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from svitlogramm.database.models.image_comments import ImageComment


async def create_comment(user_id: int, image_id: int, data: str, db: AsyncSession) -> ImageComment:
    """
    The create_comment function creates a new comment in the database.

    :param user_id: int: Specify the user_id of the comment
    :param image_id: int: Identify the image that the comment is being made on
    :param data: str: Pass the comment data to the function
    :param db: AsyncSession: Pass in the database session
    :return: A comment object
    """
    comment = ImageComment(
            user_id=user_id,
            image_id=image_id,
            data=data
        )
    db.add(comment)

    await db.commit()
    await db.refresh(comment)

    return comment


async def get_comments_by_image_or_user_id(user_id: int, image_id: int, skip: int, limit: int,
                                           db: AsyncSession) -> list[ImageComment]:
    """
    The get_comments_by_image_or_user_id function returns a list of comments for the given image and user.

    :param user_id: int: Get the comments of a specific user
    :param image_id: int: Specify the image id of the comment
    :param skip: int: Skip the first n comments
    :param limit: int: Limit the number of comments returned
    :param db: AsyncSession: Pass in the database session to use
    :return: A list of comments that match the image_id and user_id
    """
    query = select(ImageComment)

    if image_id:
        query = query.filter(ImageComment.image_id == image_id)
    if user_id:
        query = query.filter(ImageComment.user_id == user_id)

    comments = await db.scalars(query.offset(skip).limit(limit))

    return comments.all()  # noqa


async def get_comment_by_id(comment_id: int, db: AsyncSession) -> Optional[ImageComment]:
    """
    The get_comment function returns a comment object from the database.

    :param comment_id: int: Filter the comments by id
    :param db: AsyncSession: Pass the database session to the function
    :return: A comment object
    """
    return await db.scalar(
        select(ImageComment)
        .filter(ImageComment.id == comment_id)
    )


async def update_comment(comment_id: int, data: str, db: AsyncSession) -> ImageComment:
    """
    The update_comment function updates a comment in the database.

    :param comment_id: int: Find the comment in the database
    :param data: str: Update the data of a comment
    :param db: AsyncSession: Pass the database session to the function
    :return: A comment object
    """
    comment = await db.scalar(
            update(ImageComment)
            .values(data=data)
            .filter(ImageComment.id == comment_id)
            .returning(ImageComment)
        )

    await db.commit()

    return comment


async def remove_comment(comment_id: int, db: AsyncSession) -> Optional[ImageComment]:
    """
    The remove_comment function removes a comment from the database.

    :param comment_id: int: Specify the id of the comment to be removed
    :param db: AsyncSession: Pass in the database session
    :return: The comment that was removed
    """
    comment = await get_comment_by_id(comment_id, db)

    if comment:
        await db.delete(comment)
        await db.commit()

    return comment
