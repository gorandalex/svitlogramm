from fastapi import Depends, HTTPException, status

from svitlogram.database.models import UserRole, User
from svitlogram.services.auth import get_current_active_user


class UserRoleFilter:
    def __init__(self, role: UserRole) -> None:
        """
        The __init__ function is called when the class is instantiated.
        It sets the role attribute to whatever value was passed in as a parameter.

        :param self: Represent the instance of the object itself
        :param role: UserRole: Set the role of the user
        :return: Nothing
        """
        if role not in UserRole:
            raise ValueError(f"Invalid role: {role}")
        self.role = role

    async def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        The __call__ function is a decorator that allows us to use the class as a function.
        It's used in this case because we want to be able to pass the current_user into it,
        and then check if they have permission based on their role and what role they're trying
        to access.

        :param self: Access the class attributes
        :param current_user: User: Get the current user
        :return: A function that takes a current_user and returns none
        """
        if current_user.role == UserRole.admin:
            return current_user

        elif current_user.role == UserRole.moderator and self.role in [UserRole.moderator, UserRole.user]:
            return current_user

        elif current_user.role == UserRole.user and self.role == UserRole.user:
            return current_user

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access denied. Access open to \"{current_user.role}\"")
    