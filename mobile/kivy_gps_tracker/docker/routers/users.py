import os
from typing import Annotated

from .auth import check_user_name, get_current_user
import bcrypt
from db import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from model import Users
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status

BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') #salt = bcrypt.gensalt(rounds=10, prefix=b'2a')

router = APIRouter(
    prefix='/users',
    tags=['users']
)

class CreateUserRequest(BaseModel):
    user_name: str
    password: str
    role: str

class UserGetAll(BaseModel):
    user_name: str
    role: str

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
        
@router.get("/read_all", status_code=status.HTTP_200_OK, response_model=list[UserGetAll])
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    statement = select(Users.user_name, Users.role)
    result = db.execute(statement)
    users = result.all()
    return users

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    
    if check_user_name(create_user_request.user_name, db):
        raise HTTPException(status_code=401, detail='User name already exists.')    
    
    create_user_model = Users(
        user_name=create_user_request.user_name,
        role=create_user_request.role,
        password=bcrypt.hashpw(password=create_user_request.password.encode('UTF-8'), 
                               salt=BCRYPT_SALT)
    )

    db.add(create_user_model)
    db.commit()


