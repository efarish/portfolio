from db import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    password = Column(String)
    role = Column(String)