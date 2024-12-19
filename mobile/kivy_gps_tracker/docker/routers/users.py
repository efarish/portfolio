from typing import Annotated

from db import SessionLocal
from fastapi import APIRouter, Depends, HTTPException
from model import Users
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter(
    prefix='/users',
    tags=['users']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class CreateUserRequest(BaseModel):
    user_name: str
    password: str
    role: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

def check_user_name(username: str, db):

    user = db.query(Users).filter(Users.user_name == username).first()

    return True if user else False
        

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    
    if check_user_name(create_user_request.user_name, db):
        raise HTTPException(status_code=401, detail='User name already exists.')    
    
    create_user_model = Users(
        user_name=create_user_request.user_name,
        role=create_user_request.role,
        password=bcrypt_context.hash(create_user_request.password),
    )

    db.add(create_user_model)
    db.commit()
