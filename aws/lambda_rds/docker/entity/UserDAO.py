from dataclasses import dataclass
from typing import List

from db import get_db
from model import Users
from sqlalchemy.future import select


@dataclass
class User:
    id: int
    user_name: str
    role: str


def create(user_name, role, password):
    for conn in get_db():
        create_user_model = Users(
            user_name=user_name,
            role=role,
            password=password)
    conn.add(create_user_model)
    conn.commit()

def get_users() -> list[User]:
    for conn in get_db():
        statement = select(Users.id, Users.user_name, Users.role).order_by(Users.user_name)
        result = conn.execute(statement)
        users = result.all()
    return  [User(**user._asdict()) for user in users]

def create_admin_user():
    for conn in get_db():
        create_user_model = Users(
            user_name='admin',
            role='admin',
            password='a_password_')
        conn.add(create_user_model)
        conn.commit()






