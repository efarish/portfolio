from unittest import mock

import pytest as pt
from entity.user import login_for_access_token
from test_util import MockBoto3, MockTable
from util.auth import create_pwd_hash, get_current_user


@pt.mark.parametrize('user_request, user_response', 
                     [({'user_name': 'a_user', 'password':'a_password'},
                       {'user_name':'a_user', 'role':'user', 'password':create_pwd_hash('a_password').decode('UTF-8')})] )
@mock.patch('entity.user.get_client')
def test_login(mock_dao, user_request, user_response):
    mt = MockTable(query_result=[user_response])
    mb = MockBoto3(mockTable=mt)
    mock_dao.return_value = mb
    token = login_for_access_token(user_request.get('user_name'), user_request.get('password'))
    assert token
    user = get_current_user(token)
    assert user.get('user_name') == user_request.get('user_name')
    assert user.get('role') == user_response.get('role')
    current_user = get_current_user(token)
    assert current_user.get('user_name') == user_request.get('user_name')
    assert current_user.get('role') == user_response.get('role')



