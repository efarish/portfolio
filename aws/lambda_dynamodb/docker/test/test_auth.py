import sys
from unittest import mock

import pytest as pt
from test_util import MockBoto3, MockTable
from util import auth


@pt.mark.parametrize('user_request, user_response', 
                     [({'user_name': 'a_user', 'password':'a_password'},
                       {'user_name':'a_user', 'role':'user', 'password':auth.create_pwd_hash('a_password')})] )
@mock.patch('auth.UsersDAO.get_client')
def test_login(mock_dao, user_request, user_response):
    mt = MockTable(query_result=[user_response])
    mb = MockBoto3(mockTable=mt)
    mock_dao.return_value = mb
    token = auth.login_for_access_token(user_request.get('user_name'), user_request.get('password'))
    assert token
    user = auth.get_current_user(token)
    assert user.get('user_name') == user_request.get('user_name')
    assert user.get('role') == user_response.get('role')


