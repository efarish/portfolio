import importlib
import json

from routers.auth import get_current_user

from .util import *

# Imported lambda module use importlib as the directory where the lambda
#  code is stored in is called lambda. Since this a keyword, regular import
#  won't work.
lf = importlib.import_module(name=".lambda_function",package="lambda")

def get_api_override():
    return ""

def get_client_override():
    return client

lf.get_api = get_api_override
lf.get_client = get_client_override

def test_connect():
    app.dependency_overrides[get_current_user] = get_mock_user
    event = {'headers': {'authorization': 1}, 'requestContext': {'connectionId':1, 'eventType': 'CONNECT'}}
    lf.lambda_handler_websocket(event, None)

def test_disconnect():
    app.dependency_overrides[get_current_user] = get_mock_user
    event = {'headers': {'authorization': 1}, 'requestContext': {'connectionId':1, 'eventType': 'DISCONNECT'}}
    lf.lambda_handler_websocket(event, None)

def test_lambda_handler_update_location():
    app.dependency_overrides[get_current_user] = get_mock_user
    event = {'headers': {'authorization': 1}, 
             'requestContext': {'connectionId':1, 
                                'eventType': 'MESSAGE',
                                'domainName': 'bla.us-east1.com',
                                'stage': 'production'},
             'body': json.dumps({'user_name':'test', 'lat': 1.0, 'lng': 1.0 }).encode('utf-8')
             }
    lf.lambda_handler_websocket(event, None)
    
