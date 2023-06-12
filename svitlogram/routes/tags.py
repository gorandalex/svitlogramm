from typing import Any

from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session

from svitlogram.database.models import UserRole, User
from svitlogram.database.connect import get_db

from svitlogram.schemas.tag import TagUpdate, TagResponse
from svitlogram.repository import tags as repository_tags

from svitlogram.utils.filters import UserRoleFilter
from svitlogram.services.auth import get_current_active_user

router = APIRouter(prefix='/tags', tags=["tags"])


@router.post("/", response_model=list[TagResponse])
async def get_or_create_tags(
        tags: list[str] = Body(min_length=3, max_length=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_or_create_tags function is used to get or create tags.

    :param tags: Get the tags from the database
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user who is logged in
    :return: A list of tag objects
    """
    tags = await repository_tags.get_or_create_tags(tags, db)
    return tags


@router.get("/", response_model=list[TagResponse])
async def read_tags(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The read_tags function returns a list of tags.

    :param skip: int: Skip the first n tags
    :param limit: int: Limit the number of tags returned
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the current user
    :return: A list of tag objects
    """
    return await repository_tags.get_tags(skip, limit, db)


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
        tag_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_tag function is a GET request that returns the tag with the given ID.
    If no such tag exists, it raises an HTTP 404 error.

    :param tag_id: int: Get the tag id from the url
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A tag object
    """
    tag = await repository_tags.get_tag_by_id(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return tag


@router.put(
    "/",
    response_model=TagResponse,
    dependencies=[Depends(UserRoleFilter(role=UserRole.moderator))])
async def update_tag(
        body: TagUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_tag function updates a tag in the database.
        It takes an id of the tag to update, and a body containing the new data for that tag.
        The function returns an updated version of that Tag object.

    :param body: TagBase: Define the body of the request
    :param tag_id: int: Identify the tag to be deleted
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A tag object
    """
    tag = await repository_tags.update_tag(body.tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return tag


@router.delete(
    "/{tag_id}",
    response_model=TagResponse,
    dependencies=[Depends(UserRoleFilter(role=UserRole.admin))]
)
async def remove_tag(
        tag_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The remove_tag function removes a tag from the database.

    :param tag_id: int: Specify the id of the tag to be removed
    :param db: Session: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: The tag that was just deleted
    """
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

    return tag
