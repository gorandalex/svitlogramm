from typing import Optional

from pydantic import root_validator, utils

from svitlogramm.services.cloudinary import CroppingOrResizingTransformation, formatting_image_url
from .core import CoreModel, IDModelMixin, DateTimeModelMixin
from .image import ImagePublic


class ImageTransformation(CoreModel):
    """
    Model representing the complete transformation parameters for an image

    When changing the dimensions of an uploaded image by setting the image's height, width, and/or aspect ratio,
    you need to decide how to resize or crop the image to fit into the requested size. Use the c (crop/resize) parameter
    for selecting the crop/resize mode.
    """
    image_id: int
    transformation: Optional[CroppingOrResizingTransformation] = None


class FormattedImageBase(CoreModel):
    """
    Leaving salt from base model
    """
    url: str

    @root_validator(pre=True)
    def update_model(cls, values: utils.GetterDict):
        if 'url' not in values.keys():
            values._obj.url = cls.format_url(values._obj.public_id, values._obj.format)  # noqa
        return values

    @staticmethod
    def format_url(public_id: str, format_: dict):
        return formatting_image_url(public_id, format_)['url']


class FormattedImagePublic(DateTimeModelMixin, FormattedImageBase, IDModelMixin):
    class Config:
        orm_mode = True


class FormattedImageCreateResponse(CoreModel):
    parent_image_id: int
    formatted_image: FormattedImagePublic
    detail: str = "Image successfully formatted"


class ImageFormatsResponse(CoreModel):
    parent_image: ImagePublic
    formatted_images: list[FormattedImagePublic]


class ImageTransformationResponse(CoreModel):
    parent_image: ImagePublic
    formatted_image: FormattedImagePublic


class ImageFormatRemoveResponse(CoreModel):
    message: str = "Image format successfully deleted"
