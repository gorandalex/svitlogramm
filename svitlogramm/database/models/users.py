from enum import StrEnum, auto
from datetime import datetime
from typing import Optional

from sqlalchemy import String, func, event
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM

from .base import Base


class UserRole(StrEnum):
    admin = auto()
    moderator = auto()
    user = auto()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255), index=True)
    last_name: Mapped[str] = mapped_column(String(255), index=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(ENUM(UserRole, name='user_role'))
    refresh_token: Mapped[Optional[str]] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=func.now())

    @staticmethod
    def __set_user_role(mapper, connection, target):
        """
        The __set_user_role function is a SQLAlchemy event listener that will be called
        when the User model is about to be inserted into the database. The function checks
        if there are any users in the database, and if not, it sets the role of this user to admin.
        If there are already users in the database, then this user's role will be set to user.

        :param mapper: Access the mapper object for the class
        :param connection: Access the database
        :param target: Access the user object that is being saved
        :return: The target object
        """
        count = connection.execute(func.count(User.id)).scalar()

        if not count:
            target.role = UserRole.admin
        else:
            target.role = UserRole.user

    @classmethod
    def __declare_last__(cls):
        """
        The __declare_last__ function is a workaround for the fact that SQLAlchemy
        does not allow event listeners to be declared on classes which are still in
        the process of being defined.  The __declare_last__ function allows us to
        define our event listener after the class has been fully defined, but before it's used.

        :param cls: Pass the class object to the function
        """
        event.listen(cls, 'before_insert', cls.__set_user_role)
