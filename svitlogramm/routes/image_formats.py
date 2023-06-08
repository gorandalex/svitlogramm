import asyncio
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from svitlogramm.database.connect import get_db
from svitlogramm.database.models import User, UserRole
from svitlogramm.repository import images as repository_images
from svitlogramm.repository import image_formats as repository_image_formats
from svitlogramm.repository.images import get_image_by_id
from svitlogramm.schemas.image_formats import (
    ImageTransformation,
    FormattedImageCreateResponse,
    ImageFormatsResponse,
    ImageFormatRemoveResponse,
)
from svitlogramm.services import cloudinary
from svitlogramm.services.auth import get_current_active_user
from svitlogramm.services.qr_code import create_qr_for_url

router = APIRouter(prefix="/images/formats", tags=["Image formats"])


@router.post(
    '/', response_model=FormattedImageCreateResponse,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def formatting_image(
        body: ImageTransformation,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """
    The formatting_image function is used to format an image.
        The function takes in the following parameters:
            - body: ImageTransformation, which contains the id of the image and a transformation string.
            - current_user: User, which is obtained from AuthService.get_current_user(). This parameter allows us to get
                information about who made this request (the user). We use this information to ensure that only users with
                access can make requests on their own images. If no user is found, then we raise a HTTPException with status code 401 (Unauthorized) and detail &quot;

    :param body: ImageTransformation: Get the image_id and transformation parameters
    :param current_user: User: Get the user's id
    :param db: AsyncSession: Pass the database session to the repository layer
    :return: A formatted image
    """
    image = await repository_images.get_image_by_id(body.image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")
    if image.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You can't format someone else's image")

    format_image = cloudinary.formatting_image_url(image.public_id, body.transformation)

    formatted_image = await repository_image_formats.create_image_format(
        current_user.id, body.image_id, format_image['format'], db
    )
    if formatted_image is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This image already has this formatting")

    formatted_image.url = format_image['url']

    return {
        "parent_image_id": body.image_id,
        "formatted_image": formatted_image,
        "detail": "Image successfully formatted"
    }


@router.get('/{image_id}', response_model=ImageFormatsResponse, response_model_by_alias=False)
async def get_image_formats(
        image_id: int,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """
    The get_image_formats function returns a list of formatted images for the given image_id.

    :param image_id: int: Get the image by id
    :param current_user: User: Get the user id from the token
    :param db: AsyncSession: Get the database session
    :return: The original image and the formatted images
    """
    image = await repository_images.get_image_by_id(image_id, db)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image")
    if current_user.id != image.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image does not belong to you")

    image_formats = await repository_image_formats.get_image_formats_by_image_id(current_user.id, image_id, db)

    for image_format in image_formats:
        image_format.public_id = image.public_id

    return {"parent_image": image, "formatted_images": image_formats}


@router.delete("/{image_format_id}", response_model=ImageFormatRemoveResponse,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_image_format(
        image_format_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The delete_image_format function deletes an image format from the database.

    :param image_format_id: int: Get the image format by id
    :param db: AsyncSession: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A dictionary with a message
    """
    image_format = await repository_image_formats.get_image_format_by_id(image_format_id, db)

    if image_format is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found image format")

    if current_user.role != UserRole.admin and image_format.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    await repository_image_formats.remove_image_format(image_format, db)

    return {"message": "Image format successfully deleted"}


@router.get('/qr-code/{image_format_id}')
async def get_image_format_qrcode(
        image_format_id: int,
        version: Optional[int] = 1,
        box_size: Optional[int] = 10,
        border: Optional[int] = 5,
        fit: Optional[bool] = True,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
) -> Any:
    """
    The get_image_format_qrcode function is used to generate a QR code for the specified image format.

    :param image_format_id: int: Get the image format by id
    :param version: Optional[int]: Specify the version of the qr code
    :param box_size: Optional[int]: Specify the size of each box in pixels
    :param border: Optional[int]: Specify the width of the border that will be added around
    :param fit: Optional[bool]: Determine whether the qr code should be resized to fit the size of
    :param current_user: User: Get the current user from the request
    :param db: AsyncSession: Get the database session
    :return: A qr code for the image format
    """
    formatted_image = await repository_image_formats.get_image_format_by_id(image_format_id, db)
    if formatted_image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found formatted image")
    if current_user.id != formatted_image.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The image does not belong to you")

    image = await get_image_by_id(formatted_image.image_id, db)

    loop = asyncio.get_event_loop()
    qr_image = await loop.run_in_executor(
        None,
        create_qr_for_url,
        cloudinary.formatting_image_url(image.public_id, formatted_image.format)['url'],
        version,
        box_size,
        border,
        fit
    )

    return StreamingResponse(qr_image, media_type="image/png")
