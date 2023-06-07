from typing import Optional

from .core import CoreModel, DateTimeModelMixin, IDModelMixin


class ImageRatingCreate(CoreModel):
    image_id: int
    rating: int


class ImageRatingUpdate(CoreModel):
    image_id: int
    rating: Optional[int] = None


class ImageRatingResponse(DateTimeModelMixin, ImageRatingCreate, IDModelMixin):

    class Config:
        orm_mode = True
        