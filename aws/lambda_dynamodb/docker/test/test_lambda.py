import json
from unittest import mock

import lambda_function


def test_health_check():

    event = {'rawPath': '/health_check'}

    lambda_function.lambda_handler(event, None)

@mock.patch('lambda_function.UsersDAO.get_user')
def test_get_user(mock_dao):

    user = {'user_name': 'a_user'}

    mock_dao.return_value = [user]
    
    event = {'rawPath': '/get_user', 'body': '{"user_name": "a_user"}'}

    result = lambda_function.lambda_handler(event, None)

    assert result['statusCode'] == 200
    assert len(result['body']) > 0
    assert json.loads(result['body'])['user_name'] == user['user_name']


@mock.patch('lambda_function.UsersDAO.create_user')
def test_create_user(mock_dao):

    user = {'user_name': 'a_user', 'role': 'user', 'password': 'a_password'}

    mock_dao.return_value = [user]
    
    event = {'rawPath': '/create_user', 'body': f'{json.dumps(user)}'}

    result = lambda_function.lambda_handler(event, None)

    assert result['statusCode'] == 201
    assert result['body'] == f'User {user['user_name']} added.'




       
