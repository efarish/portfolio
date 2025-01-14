import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
from db import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from model import Users
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from starlette import status

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') 
ALGORITHM = 'HS256'
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

class Token(BaseModel):
    access_token: str
    token_type: str

db_dependency = Annotated[Session, Depends(get_db)]

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get('id')
        username: str = payload.get('sub')
        user_role: str = payload.get('role')
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'id': id, 'user_name': username, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    
user_dependency = Annotated[dict, Depends(get_current_user)]

async def check_user_name(username: str, db):
    statement = select(Users).where(Users.user_name == username)
    try:
        result = await db.execute(statement)
        user = result.one()[0]
    except NoResultFound:
        return None
    return user 

async def authenticate_user(username: str, password: str, db):
    user = await check_user_name(username, db) 
    if not user:
        return False
    check = bcrypt.checkpw(password=password.encode('UTF-8'), hashed_password=user.password)
    if not check:
        return False
    return user

def create_access_token(id: int, username: str, role: str, expires_delta: timedelta):
    encode = {'id': id, 'sub': username, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


@router.get("/check_token", status_code=status.HTTP_200_OK)
async def check_token(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.id, user.user_name, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}

