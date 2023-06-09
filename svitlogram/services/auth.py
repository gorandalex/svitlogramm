import pickle
from calendar import timegm
from datetime import datetime, timedelta
from typing import Optional

import redis as redis_db
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from svitlogram.database.connect import get_db
from svitlogram.repository import users as repository_users
from svitlogram.database.models import User
from config import settings


class AuthService:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key_jwt
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis = redis_db.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)

    @classmethod
    def verify_password(cls, plain_password, hashed_password) -> bool:
        """
        The verify_password function takes a plain-text password and hashed password as arguments.
        It then uses the verify method of the pwd_context object to check if they match.
        The result is returned as a boolean value.

        :param cls: Represent the class itself
        :param plain_password: Compare the password that is entered by the user to see if it matches
        :param hashed_password: Check if the password is hashed
        :return: True if the plain_password matches the hashed_password
        """
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        The get_password_hash function takes a password as input and returns the hashed version of that password.
        The hashing algorithm used is PBKDF2, which is considered secure for most applications.

        :param cls: Represent the class itself
        :param password: str: Pass in the password that is being hashed
        :return: A hashed password
        """
        return cls.pwd_context.hash(password)

    @classmethod
    def __decode_jwt(cls, token: str) -> dict:
        """
        The __decode_jwt function takes a token as an argument and returns the decoded payload.
        The decode function from the jwt library is used to decode the token, using our SECRET_KEY and ALGORITHM.

        :param cls: Represent the class itself
        :param token: str: Pass the token to the function
        :return: A dictionary with the following keys:
        """
        return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])

    @classmethod
    def __encode_jwt(cls, data: dict, iat: datetime, exp: datetime, scope: str) -> str:
        """
        The __encode_jwt function takes in a dictionary of data, an issued at time (iat),
        an expiration time (exp), and a scope. It then creates a copy of the data dictionary
        and adds the iat, exp, and scope to it. Finally it returns the encoded JWT.

        :param cls: Represent the class itself
        :param data: dict: Pass in the data that will be encoded into the jwt
        :param iat: datetime: Set the issued at time for the token
        :param exp: datetime: Set the expiration time of the token
        :param scope: str: Specify the scope of the token
        :return: A string containing the encoded jwt
        """
        to_encode = data.copy()
        to_encode.update({"iat": iat, "exp": exp, "scope": scope})

        return jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    async def create_access_token(cls, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): A dictionary of key-value pairs to be stored in the JWT payload.
                expires_delta (Optional[float]): An optional expiration time for the token, in seconds. Defaults to 15 minutes if not provided.

        :param cls: Represent the class itself
        :param data: dict: Pass the data to be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A string that is the access token
        """
        expire = datetime.utcnow() + timedelta(seconds=expires_delta or 15 * 60)
        return cls.__encode_jwt(data, datetime.utcnow(), expire, "access_token")

    @classmethod
    async def create_refresh_token(cls, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_refresh_token function creates a refresh token for the user.

        :param cls: Represent the class itself
        :param data: dict: Pass the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the time to live for the refresh token
        :return: A jwt token
        """
        expire = datetime.utcnow() + (
            timedelta(seconds=expires_delta) if expires_delta else timedelta(days=7)
        )
        return cls.__encode_jwt(data, datetime.utcnow(), expire, "refresh_token")

    @classmethod
    async def create_email_token(cls, data: dict, expires_delta: Optional[float] = None) -> str:
        """
        The create_email_token function creates a JWT token that is used to verify the user's email address.
        The function takes in two parameters: data and expires_delta. The data parameter is a dictionary containing the
        user's id, username, and email address. The expires_delta parameter specifies how long the token will be valid for;
        if it isn't specified then it defaults to one day.

        :param cls: Represent the class itself
        :param data: dict: Pass in the data that will be encoded into the jwt
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A jwt token
        """
        expire = datetime.utcnow() + (
            timedelta(seconds=expires_delta) if expires_delta else timedelta(days=1)
        )
        return cls.__encode_jwt(data, datetime.utcnow(), expire, "email_token")

    @classmethod
    async def decode_refresh_token(cls, refresh_token: str) -> str:
        """
        The decode_refresh_token function is used to decode the refresh token.
        It takes in a refresh_token as an argument and returns the email of the user who owns that token.
        If there is no scope for that token, it will raise an HTTPException with status code 401 (Unauthorized).
        If there was a JWTError, it will also raise an HTTPException with status code 401 (Unauthorized).

        :param cls: Represent the class itself
        :param refresh_token: str: Pass the refresh token to decode_refresh_token
        :return: The email of the user, if the token is valid
        """
        try:
            payload = cls.__decode_jwt(refresh_token)

            if payload.get('scope') == 'refresh_token':
                email = payload.get('sub')
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    @classmethod
    async def get_current_user(cls, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        """
        The get_current_user function is a dependency that will be used in the
            UserRouter class. It takes an access token as input and returns the user
            associated with that token. If no user is found, it raises an exception.

        :param cls: Represent the class itself
        :param token: str: Get the token from the request header
        :param db: Session: Get the database session
        :return: The user object that matches the email in the jwt
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = cls.__decode_jwt(token)

            if payload.get('scope') == 'access_token':
                email = payload.get("sub")
                if email is None or await cls.token_is_blacklist(email, token):
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = cls.redis.get(f"user:{email}")
        if user is None:

            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception

            cls.redis.set(f"user:{email}", pickle.dumps(user))
            cls.redis.expire(f"user:{email}", 900)

        else:
            user = pickle.loads(user)

        return user

    @classmethod
    async def get_email_from_token(cls, token: str) -> str:
        """
        The get_email_from_token function takes a token as an argument and returns the email associated with that token.
        It does this by decoding the JWT, checking if it has a scope of 'email_token', and then returning the subject (sub)
        of that JWT. If there is no sub or scope in the payload, or if there is no such token in our database, we raise an
        HTTPException.

        :param cls: Represent the class itself
        :param token: str: Pass the token to the function
        :return: The email address of the user who requested a password reset
        """
        try:
            payload = cls.__decode_jwt(token)

            if payload.get('scope') == 'email_token':
                email = payload.get('sub')
                return email

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    @classmethod
    async def token_is_blacklist(cls, email: str, jwt_token: str) -> bool:
        """
        The token_is_blacklist function checks if the access token is in the blacklist.
            Args:
                email (str): The user's email address.
                token (str): The user's access token.

        :param cls: Represent the class itself
        :param email: str: Get the token from redis, and the token: str parameter is used to check if it matches
        :param jwt_token: str: Check if the token is blacklisted
        :return: A boolean value
        """
        rd_token = cls.redis.get(f"black-list:{email}")

        if rd_token and jwt_token == rd_token.decode('utf-8'):
            return True

        return False

    @classmethod
    async def add_token_to_blacklist(cls, jwt_token: str) -> None:
        """
        The logout function takes an access token and adds it to the black list.
        The function first decodes the JWT, then gets the email from it.
        It also calculates how many seconds are left until expiration of that token.
        Then, we add a key-value pair to Redis where the key is "black-list:{email}" and
        the value is "access_token". We set an expiration time on this key equal to
        the number of seconds remaining until expiration.

        :param cls: Represent the class itself
        :param jwt_token: str: Get the email from the token
        :return: None
        """
        payload = cls.__decode_jwt(jwt_token)

        email: str = payload.get('sub')
        expire_seconds = payload.get('exp') - timegm(datetime.utcnow().utctimetuple())

        cls.redis.set(f"black-list:{email}", jwt_token.encode('utf-8'))
        cls.redis.expire(f"black-list:{email}", expire_seconds)
        

async def get_current_active_user(current_user: User = Depends(AuthService.get_current_user)) -> User:
    """
    The get_current_active_user function is a dependency that returns the current user,
    if it exists and is active. If not, an HTTPException with status code 400 (Bad Request)
    is raised.

    :param current_user: User: Pass the user object to the function
    :return: The current_user if it is active
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    return current_user
