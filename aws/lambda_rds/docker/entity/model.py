from datetime import datetime, timezone

from db import Base
from sqlalchemy import DECIMAL, TIMESTAMP, Column, ForeignKey, Integer, String


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class User_Location(Base):
    __tablename__ = 'user_location'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lat = Column(DECIMAL(12,8))
    lng = Column(DECIMAL(12,8))
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))