from typing import Optional
from datetime import datetime

from sqlalchemy import (
    func,
    String,
    ForeignKey,
    Integer,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .tags import Tag
from .base import Base
from .users import User
from .image_formats import ImageFormat
from .image_comments import ImageComment
from .image_raiting import ImageRating


image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1200))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped[User] = relationship(backref="images")
    tags: Mapped[Tag] = relationship("Tag", secondary=image_m2m_tag, backref="images", lazy='joined')
    comments: Mapped[ImageComment] = relationship(backref="image", cascade="all, delete-orphan")
    formats: Mapped[ImageFormat] = relationship(backref="image", cascade="all, delete-orphan")
    ratings: Mapped[ImageRating] = relationship(backref="image", cascade="all, delete-orphan")
    