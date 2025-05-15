import json
import logging
import os
from functools import wraps
from typing import Union

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv() #Need to load environment variables below reference entities.

from entity.location import UserLocation, get_user_locations, update_user_location
from entity.user import User, UserToken, create_user, get_user, login_for_access_token
from util import auth

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')))

class LoginRequest(BaseModel):
    user_name: str
    password: str

def login_handler(event) -> dict:
    body = event['body']
    try:
        user = LoginRequest.model_validate_json(body)
        user_token: UserToken = login_for_access_token(user.user_name, user.password)
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': 'Validation error.'}
    except ValueError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 403, 'body': 'Failed login.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Unexpected login failure.'}
    return {'statusCode': 200, 'body': json.dumps({"access_token": user_token.token, "token_type": "bearer"})}

def appsync_decorator(op_name: str):
    def appsync_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> dict | list[dict]:
            info = args[0]
            selectionSetList = info['selectionSetList']
            try:
                result = func(*args, **kwargs)
            except ValueError as ve:
                raise
            except Exception as e:
                logger.error(f'{e=}')
                raise Exception(f'Unexpected error occurred for [{op_name}]') from e
            if isinstance(result, list):
                response: list[dict] = [ {key: getattr(model, key) for key in selectionSetList} for model in result]
            else:
                model = result.model_dump()
                response: dict = {key: model[key] for key in selectionSetList} 
            return response
        return wrapper
    return appsync_wrapper

@appsync_decorator("Login")
def login_handler_appsync(info) -> UserToken:
    """
    Handler for creating user login.
    """
    input: dict = info['variables']
    response: UserToken = login_for_access_token(**input)
    return response
    
@appsync_decorator("Create User")
def create_user_handler(info: dict, /) -> User:
    """
    Handler for creating new users.
    """
    input: dict = info['variables']
    response: User = create_user(**input) 
    return response

@appsync_decorator("Update User Location")
def update_user_location_handler(info: dict, /) -> UserLocation:
    """
    Handler for updating user GPS location.
    """
    input: dict = info['variables']
    response: UserLocation = update_user_location(**input) 
    return response

@appsync_decorator("Get User")
def get_user_handler(info: dict, /) -> User:
    """
    Handler for retrieving a user.
    """
    user_name: str = info['variables'].get('user_name')
    response: User = get_user(user_name) 
    return response

@appsync_decorator("Get User Locations")
def get_user_locations_handler(info: dict, /) -> list[UserLocation]:
    """
    Handler for retrieving a user.
    """
    response: list[UserLocation] = get_user_locations() 
    return response

def lambda_handler_auth(event, context):
    """
    Used to authorize API GW and AppSync endpoint access.
    This checks if use token is present and valid.
    """
    headers = event['headers']
    if('authorization' not in headers):
        return {"isAuthorized": False}
    user = auth.get_current_user(headers['authorization'])
    return {"isAuthorized": bool(user)}

def lambda_handler_appsync_auth(token):
    """
    Used to authorize AppSync endpoint access.
    """
    user = auth.get_current_user(token)
    logger.debug(f'AppSync authorization for {user=}')
    return {"isAuthorized": bool(user)}
    #return {"isAuthorized": False}

def lambda_handler(event, context):
    logger.debug(f'{event=} {context=}')
    
    match event:
        case {'authorizationToken': token}:
            #This is for authorization requests from AppSync Subscriptions
            logger.debug(f'AppSync authorization handler hit.')
            return lambda_handler_appsync_auth(token)
        case {'rawPath': rawPath}: 
            #The only event taking this path should be authorizations
            # event from API GW. 
            logger.debug(f'API GW authorization handler hit: {rawPath=}')
            match rawPath:
                case '/get_user' | '/update_user_location' | '/get_user_locations':
                    response = lambda_handler_auth(event, context)
                    return response
                case _:
                    return {'statusCode': 400, 'body': f'Invalid request: {rawPath}.'}
        case {'info': info}:
            #This path is only for GraphQL.
            match info:
                case {'parentTypeName': 'Mutation', 'fieldName': 'createUser'}:
                    response = create_user_handler(info)
                    return response
                case {'parentTypeName': 'Mutation', 'fieldName': 'updateUserLocation'}:
                    response = update_user_location_handler(info)
                    return response                
                case {'parentTypeName': 'Query', 'fieldName': 'getUser'}:
                    response = get_user_handler(info)
                    return response
                case {'parentTypeName': 'Query', 'fieldName': 'getUserLocations'}:
                    response = get_user_locations_handler(info)
                    logger.info(f'getUserLocations: {response=}')
                    return response
                case {'parentTypeName': 'Query', 'fieldName': 'login'}:
                    response = login_handler_appsync(info)
                    return response
                case _:
                    raise Exception(f'Unknown operation: {info['parentTypeName']}:{info['fieldName']}')
    