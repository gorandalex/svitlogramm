from pydantic import utils, root_validator

from .core import CoreModel, IDModelMixin, DateTimeModelMixin
from .tag import TagResponse
from svitlogramm.services.cloudinary import formatting_image_url


class ImageBase(CoreModel):
    """
    Leaving salt from base model
    """
    url: str
    description: str
    tags: list[TagResponse]
    user_id: int

    @root_validator(pre=True)
    def update_model(cls, values: utils.GetterDict):
        if 'url' not in values.keys():
            values._obj.url = cls.format_url(values._obj.public_id)  # noqa
        return values

    @staticmethod
    def format_url(public_id: str):
        return formatting_image_url(public_id)['url']


class ImagePublic(DateTimeModelMixin, ImageBase, IDModelMixin):
    class Config:
        orm_mode = True


class ImageCreateResponse(CoreModel):
    image: ImagePublic
    message: str = "Image successfully uploaded"


class ImageRemoveResponse(CoreModel):
    message: str = "Image successfully deleted"