import functools

from fastapi import status
from model import Users
from routers.auth import get_current_user

from .util import *

#from routers.users import get_db


#app.dependency_overrides[get_db] = mock_get_db

def test_connect():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/connect', json={"connectionId":"1"})
    assert response.status_code == status.HTTP_201_CREATED

def test_disconnect():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/disconnect', json={"connectionId":"1"})
    assert response.status_code == status.HTTP_201_CREATED
