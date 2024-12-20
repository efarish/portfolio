from fastapi.testclient import TestClient
import main
from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from db import Base
from main import app
from routers.users import get_db, get_current_user
import pytest
from model import Users

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

@pytest.fixture
def test_user():

    user = Users()
    user.user_name = 'test_user'
    user.role = 'admin'
    user.password = 'XXXX_password'
    db = TestSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users'))
        connection.commit()

def test_read_all(test_user):
    response = client.get('/users/read_all')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [mock_get_current_user()]

