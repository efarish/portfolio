import functools

from fastapi import status
from routers.auth import get_current_user

from .util import *


def test_connect():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/connect', json={"connectionId":1})
    assert response.status_code == status.HTTP_201_CREATED

def test_disconnect():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/disconnect', json={"connectionId":1})
    assert response.status_code == status.HTTP_201_CREATED

def test_get_websocket_ids():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/connect', json={"connectionId":1})
    app.dependency_overrides[get_current_user] = get_mock_admin_user
    response = client.post('/websoc/connect', json={"connectionId":2})
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/get_websocket_ids', json={"connectionId":1})
    assert response.status_code == status.HTTP_200_OK
    web_socket_ids = response.json() 
    assert len(web_socket_ids) == 1
    assert web_socket_ids[0] == 2
