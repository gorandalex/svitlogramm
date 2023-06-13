from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from svitlogram.database.connect import get_db
from svitlogram.database.models import User, UserRole
from svitlogram.schemas.image_raitings import ImageRatingCreate, ImageRatingUpdate, ImageRatingResponse
from svitlogram.services.auth import get_current_active_user
from svitlogram.repository import image_ratings as repo_image_ratings
from svitlogram.repository import images as repository_images

router = APIRouter(prefix="/images/ratings", tags=["Image ratings"])


@router.post("/", response_model=ImageRatingResponse, status_code=status.HTTP_201_CREATED)
async def create_image_rating(
        body: ImageRatingCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
) -> Session:
    """
    The create_image_rating function creates a new image rating.

    :param body: ImageRatingCreate: Get the rating and image_id from the request body
    :param current_user: User: Get the user that is currently logged in
    :param db: Session: Get the database session
    :return: An session object
    """
    if not 1 <= body.rating <= 5:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Maximum rating is 5, minimum rating 0")

    image = await repository_images.get_image_by_id(body.image_id, db)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    if image.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot rate own image")

    rating_exist = await repo_image_ratings.get_rating_by_image_id_and_user(current_user.id, body.image_id, db)
    if rating_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already rated this image.")

    return await repo_image_ratings.create_rating(current_user.id, body.rating, body.image_id, db)


@router.put("/", response_model=ImageRatingResponse)
async def update_image_rating(
        body: ImageRatingUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_image_rating function updates the rating of an image.

    :param body: ImageRatingUpdate: Get the rating from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: An image rating object
    """
    if not 1 <= body.rating <= 5:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Maximum rating is 5, minimum rating 0")

    rating = await repo_image_ratings.get_rating_by_image_id_and_user(current_user.id, body.image_id, db)
    if rating is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")

    return await repo_image_ratings.update_rating(rating, body.rating, db)


@router.delete("/ratings/{rating_id}")
async def delete_image_rating(
        rating_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    The delete_image_rating function deletes an image rating.

    :param rating_id: int: Specify the id of the rating to be deleted
    :param current_user: User: Get the current user
    :param db: Get the database session
    :return: A dictionary with a message
    """
    rating = await repo_image_ratings.get_rating_by_id(rating_id, db)
    if not rating:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    if current_user.role != UserRole.admin or current_user.id != rating.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    await repo_image_ratings.remove_rating(rating, db)

    return {"message": "Rating deleted successfully"}


@router.get("/{image_id}/ratings")
async def get_all_image_ratings(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_all_image_ratings function returns all ratings for a given image.
        The function takes in an image_id and returns the list of ratings associated with that id.

    :param image_id: int: Get the image id from the url
    :param db: Session: Get the database session from the dependency injection container
    :param current_user: User: Get the current user who is logged in
    :return: A list of all ratings for a given image
    """
    ratings = await repo_image_ratings.get_all_image_ratings(image_id, db)

    if not ratings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ratings not found")

    return ratings
