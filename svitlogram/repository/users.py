import logging

from typing import Optional

from libgravatar import Gravatar
from sqlalchemy.orm import Session
from sqlalchemy import select, update, or_, func, RowMapping
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from svitlogram.database.models import User, UserRole, Image
from svitlogram.schemas.user import UserCreate, ProfileUpdate
from svitlogram.services.gravatar import get_gravatar


async def create_user(body: UserCreate, db: Session) -> User:
    """
    The create_user function creates a new user in the database.

    :param body: UserModel: Get the data from the request body
    :param db: Session: Pass in the database session to the function
    :return: A user object
    """
    avatar = None
    try:
        gravatar_image = Gravatar(body.email)
        avatar = gravatar_image.get_image()
    except Exception as e:
        logging.error(e)
    user = User(**body.dict(), avatar=avatar, )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


async def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """
    The get_user_by_email function returns a user object from the database
    based on the email address provided. If no user is found, None is returned.

    :param email: str: Pass the email address to the function
    :param db: Session: Pass the database session to the function
    :return: A single user or none
    """
    return db.query(User).filter(User.email == email).first()


async def get_user_by_email_or_username(email: str, username: str, db: Session) -> Optional[User]:
    """
    The get_user_by_email_or_username function returns a user object if the email or username is found in the database.

    :param email: str: Pass the email address of a user to the function
    :param username: str: Filter the database by username
    :param db: Session: Pass the database session to the function
    :return: The first user that matches the email or username
    """
    return db.query(User).filter(or_(User.email == email, User.username == username)).first()


async def get_user_by_username(username: str, db: Session) -> Optional[User]:
    """
    The get_user_by_username function returns a user object from the database based on the username.

    :param username: str: Filter the query
    :param db: Session: Pass in the database session
    :return: A user object
    """
    return db.query(User).filter(User.username == username).first()


async def get_user_by_id(user_id: int, db: Session) -> User | None:
    """
    The get_user_by_id function returns a user object from the database.

    :param user_id: int: Specify the type of the parameter
    :param db: Session: Pass the database session to the function
    :return: A single user object
    """
    return db.query(User).filter(User.id == user_id).first()


async def update_token(user: User, token: Optional[str], db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify which user the token is for
    :param token: str | None: Specify the type of token
    :param db: Session: Commit the changes to the database
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def update_avatar(user_id: int, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param user_id: int: Specify the user's id
    :param url: str: Pass the url of the avatar to be updated
    :param db: Session: Pass the database session to the function
    :return: A user object
    """
    user = await db.scalar(
        update(User)
        .values(avatar=url)
        .filter(User.id == user_id)
        .returning(User)
    )

    await db.commit()

    await db.refresh(user)

    return user


async def update_password(user_id: int, password: str, db: Session) -> User:
    """
    The update_password function updates the password of a user.

    :param user_id: int: Identify the user to update
    :param password: str: Update the password of a user
    :param db: Session: Pass the database session to the function
    :return: A user object, which is the updated user
    """


    user = await get_user_by_id(user_id, db)
    user.password = password

    db.commit()

    db.refresh(user)

    return user


async def update_email(user_id: int, email: str, db: Session) -> Optional[User]:
    """
    The update_email function updates the email of a user.

    :param user_id: int: Identify the user to update
    :param email: str: Update the email of a user
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    """
    try:
        user = await db.scalar(
            update(User)
            .values(email=email)
            .filter(User.id == user_id)
            .returning(User)
        )
        db.commit()
    except IntegrityError as e:
        return

    db.refresh(user)

    return user


async def confirmed_email(user: User, db: Session) -> None:
    """
    The confirmed_email function marks a user as confirmed in the database.

    :param user: User: Pass the user object to the function
    :param db: Session: Pass in a database session
    :return: None
    """
    user.email_verified = True
    db.commit()


async def update_user_profile(user_id: int, body: ProfileUpdate, db: Session) -> User:
    """
    The update_user_profile function updates a user's profile information.

    :param body: ProfileUpdate: Get the data from the request body
    :param user_id: int: Identify the user to update
    :param db: Session: Pass in the database session
    :return: A user object
    """
    user_body = {key: val for key, val in body.dict().items() if val is not None}

    user = await db.scalar(
        update(User)
        .where(User.id == user_id)
        .values(**user_body)
        .returning(User)
    )

    db.commit()

    db.refresh(user)

    return user


async def user_update_role(user: User, role: UserRole, db: Session) -> User:
    """
    The user_update_role function updates the role of a user.
    
    :param user: User: Identify the user that will have their role updated
    :param role: UserRole: Set the user's role to the value of role
    :param db: Session: Pass in the database session to the function
    :return: The updated user object
    """
    user.role = role
    db.commit()
    db.refresh(user)

    return user


async def user_update_is_active(user: User, is_active: bool, db: Session) -> User:
    """
    The user_update_is_active function updates the is_active field of a user.

    :param user: User: Specify the user that is being updated
    :param is_active: bool: Set the user's is_active attribute to true or false
    :param db: Session: Pass the database session to the function
    :return: The updated user
    """
    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user


async def get_user_profile_by_username(username: str, db: Session) -> RowMapping:
    """
    The get_user_profile_by_username function returns a user's profile information.

    :param username: str: Filter the user by username
    :param db: Session: Pass a database session to the function
    :return: A row mapping object
    """
    user = db.execute(
        select(User.id, User.username, User.first_name, User.last_name, User.avatar, User.created_at,
               func.count(Image.id).label('number_of_images'))
        .outerjoin(Image)
        .filter(User.username == username)
        .group_by(User.id)
    )

    return user.mappings().first()
