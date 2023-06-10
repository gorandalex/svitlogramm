import asyncio
from typing import Any

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from svitlogram.database.connect import get_db
from svitlogram.database.models import User, UserRole
from svitlogram.repository import users as repository_users
from svitlogram.schemas.user import UserPublic, ProfileUpdate

from svitlogram.schemas import user as user_schemas
from svitlogram.services import cloudinary
from svitlogram.services.auth import AuthService, get_current_active_user
from svitlogram.utils.filters import UserRoleFilter
from config import settings

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()

@router.get("/me/", response_model=user_schemas.UserPublic, dependencies=[Depends(RateLimiter(times=30, seconds=60))])
async def get_me(
        current_user: User = Depends(get_current_active_user),
        credentials: HTTPAuthorizationCredentials = Security(security)
) -> Any:
    """
    The get_me function returns the current user.

    :param current_user: User: Get the current user
    :return: The current user object
    """
    return current_user


@router.patch("/avatar", response_model=user_schemas.UserPublic,
              dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_avatar(
        file: UploadFile = File(),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_avatar function updates the avatar of a user.

    :param file: UploadFile: Get the file that is uploaded
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: The updated user object
    """
    link, public_id = current_user.avatar.rsplit('/', maxsplit=1)
    if not link.endswith(settings.cloudinary_folder):
        public_id = None

    loop = asyncio.get_event_loop()
    image = await loop.run_in_executor(
        None, cloudinary.upload_image, file.file, public_id
    )

    if image is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid image file")

    avatar = cloudinary.formatting_image_url(image['public_id'], cloudinary.FORMAT_AVATAR, image['version'])

    return await repository_users.update_avatar(current_user.id, avatar['url'], db)


@router.patch("/email", response_model=user_schemas.UserPublic,
              dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_email(
        body: user_schemas.EmailModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_email function updates the email of a user.
        The function takes in an EmailModel object, which contains the new email address to be updated.
        It also takes in a database session and current_user (the user who is making this request).

    :param body: EmailModel: Get the email from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A user object
    """
    updated_user = await repository_users.update_email(current_user.id, body.email, db)
    if updated_user is None:
        return HTTPException(status_code=status.HTTP_409_CONFLICT,
                             detail="An account with this email address already exists")

    return updated_user


@router.patch("/password", response_model=user_schemas.UserPublic,
              dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def update_password(
        body: user_schemas.UserPasswordUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_password function updates the password of a user.

    :param body: UserPasswordUpdate: Get the old and new password from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the user object from the database
    :return: A json response with the updated user
    """
    if not AuthService.verify_password(body.old_password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password")
    password = AuthService.get_password_hash(body.new_password)
    return await repository_users.update_password(current_user.id, password, db)


@router.post(
    "/change-role",
    response_model=user_schemas.UserPublic,
    dependencies=[Depends(UserRoleFilter(UserRole.admin))]
)
async def change_user_role(
        body: user_schemas.ChangeRole,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The change_user_role function is used to change the role of a user.

    :param body: user_schemas.ChangeRole: Validate the request body
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A dictionary with the user_id and role
    """
    user = await repository_users.get_user_by_id(body.user_id, db)
    print(user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role == body.role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This user already has this role installed")

    return await repository_users.user_update_role(user, body.role, db)  # noqa


@router.get("/{username}", response_model=user_schemas.UserProfile,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_user_profile(
        username: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The get_user_profile function is a GET endpoint that returns the user profile of a given username.
    It takes in an optional parameter, db, which is used to connect to the database. It also takes in another
    optional parameter, current_user, which represents the currently logged-in user.

    :param username: str: Get the username from the url
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A userprofile object
    """
    user_profile = await repository_users.get_user_profile_by_username(username, db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user_profile


@router.patch("/", response_model=user_schemas.UserPublic)
async def update_user_profile(
        body: user_schemas.ProfileUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    The update_user_profile function updates the user's profile.

    :param body: ProfileUpdate: Pass the data from the request body to this function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: A dictionary with the updated user information
    """
    if body.username and await repository_users.get_user_by_username(username=body.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="That username is already taken. Please try another one."
        )

    return await repository_users.update_user_profile(current_user.id, body, db)


@router.post("/ban/{user_id}", dependencies=[Depends(UserRoleFilter(UserRole.admin))])
async def ban_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: UserRole = Depends(get_current_active_user)
) -> Any:
    """
    The ban_user function is used to ban a user.
    :param user_id: int: Specify the user id of the user to be banned
    :param db: Session: Pass the database session to the function
    :param current_user: UserRole: Get the current user's role
    :return: A dictionary with a message, which is not the right way to return data
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return await repository_users.user_update_is_active(user, False, db)


@router.post("/unban/{user_id}", dependencies=[Depends(UserRoleFilter(UserRole.admin))])
async def unban_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: UserRole = Depends(get_current_active_user)
) -> Any:
    """
    The unban_user function is used to unban a user.

    :param user_id: int: Get the user id from the request
    :param db: Session: Get the database connection
    :param current_user: UserRole: Get the current user from the database
    :return: A dict
    """
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return await repository_users.user_update_is_active(user, True, db)
