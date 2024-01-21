from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.database import get_session, session_maker
from src.repository import get_user_by_username

KEY = "88088d1326a9357804caf831f8c7d97d3d04dcffbf36c1c382486cec6f22f564"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username, password, session):
    user = get_user_by_username(username, session)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60 * 24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, KEY, algorithm="HS256")


def get_current_user(token = Depends(OAuth2PasswordBearer(tokenUrl="/token"))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, KEY, algorithms=["HS256"])
        username = payload.get("sub", None)
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e
    user = get_user_by_username(username, session_maker())
    if user is None:
        raise credentials_exception
    return user
