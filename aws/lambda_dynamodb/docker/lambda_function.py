import json
import logging
import os
from functools import wraps

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv() #Need to load environment variables below reference entities.

from entity.user import User, create_user, get_user, login_for_access_token

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')))

class LoginRequest(BaseModel):
    user_name: str
    password: str

def login_handler(event):
    body = event['body']
    try:
        user = LoginRequest.model_validate_json(body)
        token = login_for_access_token(user.user_name, user.password)
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': 'Validation error.'}
    except ValueError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 403, 'body': 'Failed login.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Unexpected login failure.'}
    return {'statusCode': 200, 'body': json.dumps({"access_token": token, "token_type": "bearer"})}


def appsync_decorator(op_name: str):
    def appsync_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> dict:
            info = args[0]
            selectionSetList = info['selectionSetList']
            try:
                result = func(*args, **kwargs)
            except ValueError as ve:
                raise
            except Exception as e:
                logger.error(f'{e=}')
                raise Exception(f'Unexpected error occurred for [{op_name}]') from e
            user: dict = result.model_dump()
            response = {key: user[key] for key in selectionSetList} 
            return response
        return wrapper
    return appsync_wrapper

@appsync_decorator("Create User")
def create_user_handler(info: dict, /) -> User:
    """
    Handler for creating new users.
    """
    input: dict = info['variables']
    response: User = create_user(**input) 
    return response

@appsync_decorator("Get User")
def get_user_handler(info: dict, /) -> User:
    """
    Handler for retrieving a user.
    """
    user_name: str = info['variables'].get('user_name')
    response: User = get_user(user_name) 
    return response

def lambda_handler(event, context):
    logger.debug(f'{event=} {context=}')
    
    match event:
        case {'rawPath': rawPath}:
            match rawPath:
                case '/login':
                    response = login_handler(event)
                    return response
                case _:
                    return {'statusCode': 400, 'body': f'Invalid request: {rawPath}.'}
        case {'info': info}:
            match info:
                case {'parentTypeName': 'Mutation', 'fieldName': 'createUser'}:
                    response = create_user_handler(info)
                    return response                
                case {'parentTypeName': 'Query', 'fieldName': 'getUser'}:
                    response = get_user_handler(info)
                    return response
                case _:
                    raise Exception(f'Unknown operation: {info['parentTypeName']}:{info['fieldName']}')
    