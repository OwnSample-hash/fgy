import os
import jwt
from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pydantic import BaseModel

from db.models import UserSchema


from .hash import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, create_access_token, hash_password, verify_password
from db import db, User, redis

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ["JWT_KEY"], algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception
    with db.query_first(User, username=token_data.username) as user:
        if user is None:
            raise credentials_exception
        return UserSchema.model_validate(user)

async def get_current_active_user(
    current_user: Annotated[UserSchema, Depends(get_current_user)],
):
    return current_user

@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    with db.query_first(User, username = form_data.username) as user:
        db.logger.info(user)
        if not user or verify_password(form_data.password, user.password) is False:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password"
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token, tid = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        redis.setex(f"token:{tid}", user.id, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        return Token(access_token=access_token, token_type="bearer")

@router.post("/register")
async def register(username: str, password: str, email: str):
    with db.query_first(User, username = username) as user:
        if user:    
            db.logger.warning(f"Attempt to register existing username: {username}")
            raise HTTPException(
                status_code=400,
                detail="Username already registered"
            )
    new_user = User(username=username, email=email, password=hash_password(password))
    db.insert(new_user)
    return {"msg": "User created successfully"}


@router.post("/user/me", response_model=UserSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user 
