import json
from typing import Set

from pydantic import validator
from .core import CoreModel, IDModelMixin, DateTimeModelMixin


class TagBase(CoreModel):
    name: str


class TagUpdate(TagBase):
    tag_id: int


class TagResponse(DateTimeModelMixin, TagBase, IDModelMixin):

    class Config:
        orm_mode = True
        

