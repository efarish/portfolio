from db import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class User_Location(Base):
    __tablename__ = 'user_location'

    id = Column(Integer, primary_key=True, index=True)