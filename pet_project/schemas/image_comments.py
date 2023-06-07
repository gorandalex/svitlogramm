from pydantic import constr

from .core import CoreModel, DateTimeModelMixin, IDModelMixin


class CommentBase(CoreModel):
    image_id: int
    data: constr(min_length=5, max_length=500)


class CommentUpdate(CoreModel):
    comment_id: int
    data: constr(min_length=5, max_length=500)


class CommentPublic(DateTimeModelMixin, CommentBase, IDModelMixin):
    user_id: int

    class Config:
        orm_mode = True
        