import os

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db import Base
from main import app
from model import Users

BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') 

def get_mock_admin_user():
    return {'user_name': 'test_user',
            'role': 'admin'}

def get_mock_user():
    return {'user_name': 'test_user',
            'role': 'user'}

@pytest.fixture
def insert_user(request):
    user = Users()
    mock_user = request.param
    user.user_name = mock_user['user_name']
    user.role = mock_user['role']
    user.password = bcrypt.hashpw(password='XXXX_password'.encode('UTF-8'), salt=BCRYPT_SALT)
    db = TestSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users'))
        connection.commit()

DB_URL = 'sqlite:///./testdb.db'

engine = create_engine(DB_URL, 
                       connect_args={"check_same_thread": False},
                       poolclass=StaticPool,)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def mock_get_db():
    db = TestSessionLocal() 
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)
