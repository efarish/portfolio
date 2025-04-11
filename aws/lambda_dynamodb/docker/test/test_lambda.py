import json
from unittest import mock

import lambda_function
import pytest as pt


def test_health_check():

    event = {'rawPath': '/health_check'}

    lambda_function.lambda_handler(event, None)


@pt.mark.parametrize('user_request, user_response, expected_status', 
                     [({'user_name': 'a_user'},
                       {'user_name': 'a_user', 'role':'user', 'password':'a_password'},200),
                      ({'user': 'a_user'},None,400), 
                      ])
@mock.patch('lambda_function.UsersDAO.get_user')
def test_get_user(mock_dao, user_request, user_response, expected_status):

    mock_dao.return_value = [user_response]
    
    event = {'rawPath': '/get_user', 'body': f'{json.dumps(user_request)}'}

    result = lambda_function.lambda_handler(event, None)

    assert result['statusCode'] == expected_status 
    
    if result['statusCode'] == 200:
        assert len(result['body']) > 0
        assert json.loads(result['body'])['user_name'] == user_response['user_name']


@pt.mark.parametrize('user, expected', 
                     [({'user_name': 'a_user', 'role': 'user', 'password': 'a_password'},(201, 'User a_user added.')),
                      ({'user_name': 'a_user',                 'password': 'a_password'},(400, 'Validation error.')), 
                      ])
@mock.patch('lambda_function.UsersDAO.create_user')
def test_create_user(mock_dao, user, expected):

    mock_dao.return_value = [user]
    
    event = {'rawPath': '/create_user', 'body': f'{json.dumps(user)}'}

    result = lambda_function.lambda_handler(event, None)

    assert result['statusCode'] == expected[0]
    assert result['body'] == expected[1]




       
