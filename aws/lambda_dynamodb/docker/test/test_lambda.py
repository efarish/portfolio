import json
from unittest import mock

import lambda_function
import pytest as pt
from test_util import MockBoto3, MockTable

"""
def test_health_check():

    event = {'rawPath': '/health_check'}

    lambda_function.lambda_handler(event, None)
        
"""
"""
@pt.mark.parametrize('user, expected', 
                     [({'user_name': 'a_user', 'role': 'user', 'password': 'a_password'},(201, 'User a_user added.')),
                      ({'user_name': 'a_user',                 'password': 'a_password'},(400, 'Validation error.')), 
                      ])
@mock.patch('entity.user.get_client')
def test_create_user(mock_dao, user, expected):

    if len(user) == 3:
        mb = MockBoto3(mockTable=MockTable(query_result=user))
        mock_dao.return_value = mb    
    
    event = {'rawPath': '/create_user', 'body': f'{json.dumps(user)}'}

    result = lambda_function.lambda_handler(event, None)

    assert result['statusCode'] == expected[0]
    assert result['body'] == expected[1]
"""
    
@pt.mark.parametrize('user_request, user_response, expected_status', 
                     [({'user_name': 'a_user'},
                       {'user_name':'a_user', 'role':'user', 'password':'a_password'},200),
                      ({'user': 'a_user'},{'user_name':'a_user', 'role':'user', 'password':'a_password'},400), 
                      ])
@mock.patch('lambda_function.get_current_user')
@mock.patch('entity.user.get_client')
def test_get_user(mock_dao, mock_user, user_request, user_response, expected_status):

    mt = MockTable(query_result=[user_response])
    mb = MockBoto3(mockTable=mt)
    mock_dao.return_value = mb

    mock_user.return_value = user_response
    
    """
    event = {'rawPath': '/get_user', 
             'headers': {'authorization': 'Bearer a token'},
             'body': f'{json.dumps(user_request)}'}
    """
    event = {'info': {'parentTypeName': 'Query', 
                      'fieldName': 'getUser', 
                      'variables': {'user_name': 'a_user'},
                      'selectionSetList': ['user_name', 'role', 'password']
                    }
            }
             
    result = lambda_function.lambda_handler(event, None)

    assert isinstance(result, dict) 

    assert len(result) == 3 

    """
    assert result['statusCode'] == expected_status 
    
    if result['statusCode'] == 200:
        assert len(result['body']) > 0
        assert json.loads(result['body'])['user_name'] == user_response['user_name']
    """