from typing import List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from svitlogram.database.connect import get_db
from svitlogram.database.models import UserRole, User
from svitlogram.schemas.image_comments import CommentBase, CommentPublic, CommentUpdate
from svitlogram.repository import comments as repository_comments
from svitlogram.repository import images as repository_images
from svitlogram.utils.filters import UserRoleFilter
from svitlogram.services.auth import get_current_active_user


router = APIRouter(prefix='/images/comments', tags=["Image comments"])


@router.post("/", response_model=CommentPublic, status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentBase,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The create_comment function creates a new comment in the database.

    :param body: CommentBase: Get the body of the comment
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Get the user who is currently logged in
    :return: A comment object
    """
    image = await repository_images.get_image_by_id(body.image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    return await repository_comments.create_comment(
        current_user.id, body.image_id, body.data.strip(), db
    )


@router.get(
    '/',
    response_model=List[CommentPublic],
    description='No more than 10 requests per minute',
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def get_comments_by_image_or_user_id(
        image_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_comments_by_image_or_user_id function is used to get comments by image_id or user_id.
        Args:
            image_id (int): The id of the image that you want to retrieve comments for.
            user_id (int): The id of the user that you want to retrieve comments for.

    :param image_id: Optional[int]: Specify the image id
    :param user_id: Optional[int]: Specify the user_id of the comment to be deleted
    :param skip: int: Skip the first n comments
    :param limit: int: Limit the number of comments that are returned
    :param db: Session: Get the database connection
    :param current_user: User: Get the current user from the database
    :return: A list of comments
    """
    if user_id is None and image_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Both user_id or image_id must be provided")

    return await repository_comments.get_comments_by_image_or_user_id(
        user_id, image_id, skip, limit, db
    )


@router.get("/{comment_id}", response_model=CommentPublic)
async def get_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_comment function returns a comment by its id.

    :param comment_id: int: Get the comment id from the url path
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A comment object
    """
    comment = await repository_comments.get_comment_by_id(comment_id, db)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return comment


@router.put("/", response_model=CommentPublic)
async def update_comment(
        body: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_comment function updates a comment in the database.
        The function takes an id of the comment to be updated, and a CommentUpdate object containing
        the new values for each field.

    :param body: CommentUpdate: Pass the new comment body to the function
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The updated comment
    """
    comment = await repository_comments.update_comment(body.comment_id, body.data, db)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ImageComment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Comment update is allowed only for user that create comment")

    return comment


@router.delete('/{comment_id}', dependencies=[Depends(UserRoleFilter(UserRole.moderator))])
async def remove_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The remove_comment function removes a comment from the database.
        The function takes in an integer representing the id of the comment to be removed,
        and returns a dictionary containing information about that comment.

    :param comment_id: int: Specify the id of the comment that is to be deleted
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user that is currently logged in
    :return: A comment
    """
    comment = await repository_comments.remove_comment(comment_id, db)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return comment