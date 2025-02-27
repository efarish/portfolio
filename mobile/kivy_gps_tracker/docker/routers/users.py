import os
from typing import Annotated

import bcrypt
from db import get_db
from fastapi import APIRouter, Depends, HTTPException, Path
from model import Users
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from starlette import status

from .auth import check_user_name, user_dependency

BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') 

router = APIRouter(
    prefix='/users',
    tags=['users']
)

class CreateUserRequest(BaseModel):
    user_name: str
    password: str
    role: str

class UpdateUserRequest(BaseModel):
    role: str

class UserGetAll(BaseModel):
    id: int
    user_name: str
    role: str

    class Config:
        from_attributes = True

db_dependency = Annotated[Session, Depends(get_db)]
        
@router.get("/read_all", status_code=status.HTTP_200_OK, response_model=list[UserGetAll])
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    statement = select(Users.id, Users.user_name, Users.role)
    result = await db.execute(statement)
    users = result.all()
    return users

async def create_user_util(db, create_user_request):
    user = await check_user_name(create_user_request.user_name, db)
    if user:
        raise HTTPException(status_code=401, detail='User name already exists.')    
    create_user_model = Users(
        user_name=create_user_request.user_name,
        role=create_user_request.role,
        password=bcrypt.hashpw(password=create_user_request.password.encode('UTF-8'), 
                               salt=BCRYPT_SALT)
    )
    db.add(create_user_model)
    await db.commit()

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
        
    await create_user_util(db, create_user_request)

@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency,
                      update_user_request: UpdateUserRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    statement = select(Users).where(Users.id == user.get('id'))
    try:
        result = await db.execute(statement)
        user_model = result.one()[0]
    except NoResultFound:
        raise HTTPException(status_code=404, detail='User not found.')
    user_model.role = update_user_request.role
    db.add(user_model)
    await db.commit()

@router.delete("/delete/{user_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_name: str = Path(..., min_length=1)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    statement = delete(Users).where(Users.user_name == user_name)
    result = await db.execute(statement)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail='Delete failed.')
    await db.commit()