import pytest
from jose import JWTError, jwt
from routers.auth import get_current_user

from .util import *


@pytest.mark.asyncio
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
    assert user['user_name'] == 'test_user'
    assert user['role'] == 'admin'


