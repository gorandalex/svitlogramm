from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from svitlogram.database.models.base import Base
from svitlogram.database.models.users import User


class ImageRating(Base):
    __tablename__ = "image_ratings"
    __table_args__ = (
        UniqueConstraint('user_id', 'image_id', name='unique_user_image_rating'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    rating: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE", onupdate="CASCADE"))
    image_id: Mapped[int] = mapped_column(ForeignKey("images.id", ondelete="CASCADE", onupdate="CASCADE"))

    user: Mapped[User] = relationship("User", backref="image_ratings")