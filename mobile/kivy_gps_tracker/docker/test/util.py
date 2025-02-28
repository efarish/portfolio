import os

import bcrypt
import pytest
from db import Base
from fastapi.testclient import TestClient
from main import app
from model import User_Location, Users
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') 

def get_mock_admin_user(id: int = 1):
    return {'id': id, 'user_name': 'test_admin_user',
            'role': 'admin'}

def get_mock_user(id: int = 2):
    return {'id': id, 'user_name': 'test_user',
            'role': 'user'}

def get_mock_user_location(id: int = 1, user_id = 2):
    return {'id': id, 'user_id': user_id,
            'lat': 1.0, 'lng': 1.0}

def get_mock_user_location_2(id: int = 2, user_id = 2):
    return {'id': id, 'user_id': user_id,
            'lat': 2.0, 'lng': 2.0}

def get_mock_user_2(id: int = 3):
    return {'id': id, 'user_name': 'test_user_2',
            'role': 'user'}

@pytest.fixture(scope="function")
def insert_user(request):
    user = Users()
    mock_user = request.param
    user.id = mock_user['id']
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

@pytest.fixture(scope="function")
def insert_users(request):
    mock_user_list = request.param
    for mock_user in mock_user_list:
        user = Users()
        user.id = mock_user['id']
        user.user_name = mock_user['user_name']
        user.role = mock_user['role']
        user.password = bcrypt.hashpw(password='XXXX_password'.encode('UTF-8'), salt=BCRYPT_SALT)
        db = TestSessionLocal()
        db.add(user)
        db.commit()
    yield mock_user_list
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users'))
        connection.commit()

@pytest.fixture(scope="function")
def insert_location(request):
    user = Users()
    mock_user = request.param['user']
    user.id = mock_user['id']
    user.user_name = mock_user['user_name']
    user.role = mock_user['role']
    db = TestSessionLocal()
    db.add(user)

    loc = User_Location()
    mock_location = request.param['loc']
    loc.user_id = mock_location['user_id']
    loc.lat = mock_location['lat']
    loc.lng = mock_location['lng']
    db.add(loc)
    db.commit()
    
    yield user, loc
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM user_location'))
        connection.execute(text('DELETE FROM users'))
        connection.commit()

# SQLite connection for test suite.
DB_URL = 'sqlite:///./testdb.db'
engine = create_engine(DB_URL,connect_args={"check_same_thread": False}, poolclass=StaticPool,)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Mock SQLite connection for application code. 
DB_URL_ASYNC = 'sqlite+aiosqlite:///./testdb.db'
engine_async = create_async_engine(DB_URL_ASYNC, connect_args={'check_same_thread': False}, poolclass=StaticPool,)
TestSessionLocal_Async= sessionmaker(bind=engine_async, autocommit=False, autoflush=False, 
                                     expire_on_commit=False, class_=AsyncSession) 

async def mock_get_db():
    async with TestSessionLocal_Async() as session:
        yield session

client = TestClient(app)
