import uuid
import enum

from typing import BinaryIO, Optional

import cloudinary
from cloudinary.uploader import upload
from pydantic import BaseModel

from config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)


class CropMode(enum.StrEnum):
    """
    Enum representing different modes of cropping

    If the requested dimensions have a different aspect ratio than the original, these modes crop out part of the image.
    """
    FILL = 'fill'
    """Resizes the image to fill the specified dimensions without distortion. The image may be cropped as a result."""
    IFILL = 'ifill'
    """Same as fill, but only scales down the image."""
    FILL_PAD = 'fill_pad'
    """Same as fill, but avoids excessive cropping by adding padding when needed. Supported only with automatic 
    cropping."""
    CROP = 'crop'
    """Extracts a region of the specified dimensions from the original image without first resizing it."""
    THUMB = 'thumb'
    """
    Creates a thumbnail of the image with the specified dimensions, based on a specified gravity. Scaling may occur.
    """

    """These modes adjust the size and/or crop the image using an add-on."""
    IMAGGA_SCALA = 'imagga_scala'
    """Performs smart scaling, using the Imagga Crop and Scale add-on."""
    IMAGGA_CROP = 'imagga_crop'
    """Performs smart cropping, using the Imagga Crop and Scale add-on."""


class ResizeMode(enum.StrEnum):
    """
    Enum representing different modes of resizing

    These modes adjust the size of the delivered image without cropping out any elements of the original image.
    """
    SCALE = 'scale'
    """Resizes the image to the specified dimensions without necessarily retaining the original aspect ratio."""
    FIT = 'fit'
    """Resizes the image to fit inside the bounding box specified by the dimensions, maintaining the aspect ratio."""
    LIMIT = 'limit'
    """Same as fit, but only scales down the image."""
    M_FIT = 'm_fit'
    """Same as fit, but only scales up the image."""
    PAD = 'pad'
    """Resizes the image to fit inside the bounding box specified by the dimensions, maintaining the aspect ratio, 
    and applies padding if the resized image does not fill the whole area."""
    IPAD = 'ipad'
    """Same as pad, but only scales down the image."""
    MPAD = 'mpad'
    """Same as pad, but only scales up the image."""

    """These modes adjust the size and/or crop the image using an add-on."""
    IMAGGA_SCALA = 'imagga_scala'
    """Performs smart scaling, using the Imagga Crop and Scale add-on."""
    IMAGGA_CROP = 'imagga_crop'
    """Performs smart cropping, using the Imagga Crop and Scale add-on."""


class GravityMode(enum.StrEnum):
    """Enum representing the gravity of the cropped image"""
    CENTER = 'center'
    NORTH = 'north'
    NORTH_WEST = 'north_west'
    NORTH_EAST = 'north_east'
    SOUTH = 'south'
    SOUTH_WEST = 'south_west'
    SOUTH_EAST = 'south_east'
    WEST = 'west'
    EAST = 'east'


class CroppingOrResizingTransformation(BaseModel):
    """Model representing the parameters for cropping or resizing an image"""
    width: Optional[int] = None
    height: Optional[int] = None
    crop: Optional[CropMode | ResizeMode] = None
    gravity: Optional[GravityMode] = None


def upload_image(file: BinaryIO, public_id: Optional[str] = None) -> Optional[dict]:
    """
    The upload_image function uploads an image to Cloudinary.

    :param file: BinaryIO: Pass the image file to be uploaded
    :param public_id: Optional[str]: Set a custom name for the image
    :return: A tuple of three values:
    """
    try:
        image = cloudinary.uploader.upload_image(
            file=file,
            public_id=public_id or uuid.uuid4().hex,
            folder=settings.cloudinary_folder,
            owerwrite=True,
        )
    except cloudinary.exceptions.Error:
        return

    return {'url': image.url, 'public_id': image.public_id, 'version': image.version}


def formatting_image_url(public_id: str,
                         transformation: Optional[CroppingOrResizingTransformation | dict] = None,
                         version: Optional[str] = None) -> Optional[dict]:
    """
    The formatting_image_url function takes in a file_id, and transformation, version.
    The function then returns the url of the image with the specified transformation applied to it.

    :param public_id: str: Specify the public_id of the image
    :param transformation: Optional[CroppingTransformation | ResizingTransformation]: Specify the type of transformation to be applied on the image
    :param version: Optional[str]: Specify the version of the image to be used
    :return: A dictionary with the transformation parameters
    """
    if isinstance(transformation, CroppingOrResizingTransformation):
        transformation = transformation.dict()

    image = cloudinary.CloudinaryImage(
        public_id=public_id,
        version=version,
        url_options=transformation
    )

    return {'url': image.url, 'format': image.url_options}


def remove_image(public_id: str) -> bool:
    """
    The remove_image function takes in a public_id string and returns True if the image was successfully removed from
    Cloudinary. If the image is not found, or there is an error removing it, False will be returned.

    :param public_id: str: Specify the public id of the image to be deleted
    :return: A boolean value indicating whether the image was successfully removed
    """
    result = cloudinary.uploader.destroy(public_id=public_id)
    if result['result'] == "ok":
        return True

    return False


FORMAT_AVATAR = CroppingOrResizingTransformation(
    crop=CropMode.FILL,
    width=250,
    height=250,
)
