import os
import jwt
import random
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    return password_hasher.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    tid = random.randint(10000000, 99999999)
    to_encode.update({"exp": expire, "tid": tid})
    encoded_jwt = jwt.encode(to_encode, os.environ["JWT_KEY"], algorithm=ALGORITHM)
    return encoded_jwt, tid
