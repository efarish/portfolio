import pytest
from jose import JWTError, jwt
from routers.auth import get_current_user

from .util import *


@pytest.mark.asyncio
async def test_token(test_admin_user):

    response = client.post('/auth/token',
                           data={'username': 'test_user', 'password': 'XXXX_password'})
    assert response.status_code == 200
    data = response.json()
    print(data)
    user = await get_current_user(data['access_token'])
    assert user['username'] == 'test_user'
    assert user['role'] == 'admin'


