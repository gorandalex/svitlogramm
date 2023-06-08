from .core import CoreModel, IDModelMixin, DateTimeModelMixin


class TagBase(CoreModel):
    name: str


class TagUpdate(TagBase):
    tag_id: int


class TagResponse(DateTimeModelMixin, TagBase, IDModelMixin):

    class Config:
        orm_mode = True
        