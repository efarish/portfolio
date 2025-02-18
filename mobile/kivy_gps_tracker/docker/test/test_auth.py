import pytest
from routers.auth import get_current_user, get_db

from .util import *

app.dependency_overrides[get_db] = mock_get_db

@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    'insert_user',
    [get_mock_admin_user()],
    indirect=True
)
async def test_token(insert_user):
    response = client.post('/auth/token',
                           data={'username': insert_user.user_name, 
                                 'password': 'XXXX_password'})
    assert response.status_code == 200
    data = response.json()
    user = await get_current_user(data['access_token'])
    assert user['id'] == 1
    assert user['user_name'] == 'test_admin_user'
    assert user['role'] == 'admin'

@pytest.mark.parametrize(
    'insert_user',
    [get_mock_admin_user()],
    indirect=True
)
def test_check_token(insert_user):
    response1 = client.post('/auth/token',
                           data={'username': insert_user.user_name, 
                                 'password': 'XXXX_password'})
    assert response1.status_code == 200
    data1 = response1.json()
    headers = {"Authorization": f"Bearer {data1['access_token']}", "Content-Type": "application/json"}
    response2 = client.get('/auth/check_token', headers=headers)
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2['id'] == insert_user.id
    assert data2['user_name'] == insert_user.user_name

@pytest.mark.parametrize(
    'insert_user',
    [get_mock_admin_user()],
    indirect=True
)
def test_check_token_failed_1(insert_user):
    response = client.get('/auth/check_token')
    assert response.status_code == 401

@pytest.mark.parametrize(
    'insert_user',
    [get_mock_admin_user()],
    indirect=True
)
def test_check_token_failed_2(insert_user):
    headers = {"Authorization": f"Bearer blabla", "Content-Type": "application/json"}
    response = client.get('/auth/check_token', headers=headers)
    assert response.status_code == 401




