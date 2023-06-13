import asyncio
import mimetypes
from typing import Optional, Any

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query, Body
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from svitlogram.database.connect import get_db
from svitlogram.database.models import User, UserRole
from svitlogram.repository import images as repository_images, tags as repository_tags
from svitlogram.schemas.image import ImageCreateResponse, ImagePublic, ImageRemoveResponse
from svitlogram.services import cloudinary
from svitlogram.services.auth import get_current_active_user
from .docs import images as docs

router = APIRouter(prefix="/images", tags=["Images"])

allowed_content_types_upload = [
    ".ai",
    ".gif",
    ".png",
    ".webp",
    ".avif",
    ".jfif",
    ".bmp",
    ".bw",
    ".dng",
    ".ps",
    ".ept",
    ".eps",
    ".eps3",
    ".fbx",
    ".flif",
    ".glb",
    ".gltf",
    ".heif",
    ".heic",
    ".ico",
    ".indd",
    ".jpg",
    ".jpe",
    ".jpeg",
    ".jp2",
    ".wdp",
    ".jxr",
    ".hdp",
    ".obj",
    ".pdf",
    ".ply",
    ".png",
    ".psd",
    ".arw",
    ".cr2",
    ".svg",
    ".tga",
    ".tif",
    ".tiff",
    ".u3ma",
    ".usdz",
    ".webp",
    ]


@router.post(
    "/", response_model=ImageCreateResponse, response_model_by_alias=False, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]
)
async def upload_image(
        file: UploadFile = File(), 
        description: str = Form(min_length=10, max_length=1200),
        tags: Optional[list[str]] = Form(None),
        # tags = Form(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user),
) -> Any:  
    """
    The upload_image function is used to upload an image file to the cloudinary server.
    The function takes in a file, description and tags as parameters. The file parameter is of type UploadFile which
    is a FastAPI class that represents uploaded files. The description parameter is of type str and has minimum length
    of 10 characters and maximum length of 1200 characters while the tags parameter is optional with each tag having
    minimum length 3 characters and maximum 50 characters.

    :param file: UploadFile: Receive the image file from the client
    :param description: str: Get the description of the image from the request body
    :param tags: Optional[list[str]]: Validate the tag list
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user that is logged in
    :param : Get the image id from the url
    :return: A dictionary with the image and detail keys
    """
    # try:
    #     tags = {tag.strip() for tag in tags.split(',')}
    # except:
    #     ...
    
    if mimetypes.guess_extension(file.content_type,) not in allowed_content_types_upload:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Invalid file type. Only allowed {allowed_content_types_upload}.")
    
    tags = repository_tags.get_list_tags(tags)

    if tags and len(tags) > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Maximum five tags can be added")

    if tags:
        print(tags)
        for tag in tags:
            if not 3 <= len(tag) <= 50:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail=f'Invalid length tag: {tag}')

    loop = asyncio.get_event_loop()
    image = await loop.run_in_executor(None, cloudinary.upload_image, file.file)

    if image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid image file")

    image = await repository_images.create_image(current_user.id, description.strip(), tags, image['public_id'], db)

    return {"image": image, "message": "Image successfully uploaded"}


@router.get("/", response_model=list[ImagePublic], description="Get all images",
            )#dependencies=[Depends(RateLimiter(times=300, seconds=60))]
async def get_images(
        skip: int = 0,
        limit: int = Query(default=10, ge=1, le=100),
        description: Optional[str] = Query(default=None, min_length=3, max_length=1200),
        tags: Optional[list[str]] = Query(default=None, max_length=50),
        image_id: Optional[int] = Query(default=None, ge=1),
        user_id: Optional[int] = Query(default=None, ge=1),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_images function is used to retrieve images from the database.
        The function takes in a skip, limit, description, tags and user_id as parameters.
        The skip parameter is used to determine how many images should be skipped before returning results.
        The limit parameter determines how many results should be returned after skipping the specified number of images.
        If no value for limit is provided then 10 will be assumed by default (max 100).

    :param skip: int: Skip a number of images when returning the list
    :param limit: int: Limit the number of images returned
    :param description: Optional[str]: Filter the images by description
    :param tags: Optional[list[str]]: Filter the images by tags
    :param image_id: Optional[int]: Get the image by id
    :param user_id: Optional[int]: Filter the images by user_id
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A list of images
    """
    return await repository_images.get_images(skip, limit, description, tags, image_id, user_id, db)


@router.get("/{image_id}", response_model=ImagePublic)
async def get_image(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_image function returns an image by its id.

    :param image_id: int: Get the image id from the url
    :param db: AsyncSession: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The image object
    """
    image = await repository_images.get_image_by_id(image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    return image


@router.patch("/", response_model=ImagePublic, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_image_data(
        image_id: int = Body(ge=1),
        description: str = Body(min_length=10, max_length=1200),
        tags: Optional[list[str]] = Body(None, min_length=3, max_length=50),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_description function updates the description of an image.

    :param image_id: int: Identify the image that we want to delete
    :param description: str: Update the description of an image
    :param tags: Optional[list[str]]: Get the tags from the request body
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: An image with a new description and tags
    """
    if tags and len(tags) > 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Maximum five tags can be added")

    image = await repository_images.get_image_by_id(image_id, db)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    if current_user.role != UserRole.admin and image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updated_image = await repository_images.update_description(image_id, description, tags, db)

    return updated_image


@router.delete("/{image_id}", response_model=ImageRemoveResponse,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_image(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The delete_image function deletes an image from the database and cloudinary.

    :param image_id: int: Get the image id from the url
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user
    :return: A dictionary with the message key and value
    """
    image = await repository_images.get_image_by_id(image_id, db)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")

    if current_user.role != UserRole.admin and image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, cloudinary.remove_image, image.public_id)
    await repository_images.delete_image(image, db)

    return {"message": "Image successfully deleted"}
