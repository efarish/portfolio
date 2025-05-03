from unittest import mock

import lambda_function
import pytest as pt
from test_util import MockBoto3, MockTable


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
    assert len(result) == 4
    assert result['__typename'] == 'User'