import os

import bcrypt
import main
import pytest
from db import Base
from fastapi.testclient import TestClient
from main import app
from model import Users
from routers.users import get_current_user, get_db
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BCRYPT_SALT = os.getenv('BCRYPT_SALT').encode('UTF-8') 

@pytest.fixture
def test_admin_user():

    user = Users()
    user.user_name = 'test_user'
    user.role = 'admin'
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
                       poolclass=StaticPool,
                       )

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def mock_get_db():
    db = TestSessionLocal() 
    try:
        yield db
    finally:
        db.close()

def mock_get_current_user():
    return {'user_name': 'test_user',
            'role': 'admin'}

app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(main.app)
