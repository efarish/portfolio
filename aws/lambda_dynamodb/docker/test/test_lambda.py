from unittest import mock

import lambda_function
import pytest as pt
from test_util import MockBoto3, MockTable
from util.auth import create_pwd_hash


@pt.mark.parametrize('user_request', 
                     [({'user_name': 'a_user', 'role': 'user', 'password': create_pwd_hash('a_password').decode('UTF-8')}),])
@mock.patch('entity.user.get_client')
def test_login_handler(mock_dynamodb_client, user_request):
    
    mt = MockTable(query_result=[user_request])
    mb = MockBoto3(mockTable=mt)
    mock_dynamodb_client.return_value = mb

    mock_event = {'rawPath': '/login',
                  'body': '{"user_name": "a_user", "password": "a_password"}'}
    result = lambda_function.lambda_handler(mock_event, None)
    assert isinstance(result, dict)
    assert result['statusCode'] == 200
    

@pt.mark.parametrize('user_request, selection_list', 
                     [({'user_name': 'a_user', 'role': 'user', 'password': 'password'},
                       ['user_name', 'role', 'password']),])
@mock.patch('entity.user.get_client')
def test_create_user(mock_dynamodb_client, user_request, selection_list):

    mt = MockTable(query_result=[user_request])
    mb = MockBoto3(mockTable=mt)
    mock_dynamodb_client.return_value = mb
 
    event = {'info': {'parentTypeName': 'Mutation', 
                      'fieldName': 'createUser', 
                      'variables': user_request,
                      'selectionSetList': selection_list
                    }
            }
             
    result = lambda_function.lambda_handler(event, None)

    assert isinstance(result, dict) 
    assert len(result) == 3


@pt.mark.parametrize('user_request, selection_list, get_user_response', 
                     [({'user_name': 'a_user'},['user_name', 'role', 'password'],
                       {'user_name':'a_user', 'role':'user', 'password':'a_password'}),
                      ({'user': 'a_user'},['user_name', 'role', 'password'],
                       {'user_name':'a_user', 'role':'user', 'password':'a_password'}), 
                      ])
@mock.patch('entity.user.get_client')
def test_get_user(mock_dynamodb_client, user_request, selection_list, get_user_response):

    mt = MockTable(query_result=[get_user_response])
    mb = MockBoto3(mockTable=mt)
    mock_dynamodb_client.return_value = mb
    
    event = {'info': {'parentTypeName': 'Query', 
                      'fieldName': 'getUser', 
                      'variables': user_request,
                      'selectionSetList': selection_list
                    }
            }
             
    result = lambda_function.lambda_handler(event, None)

    assert isinstance(result, dict) 
    assert len(result) == 3