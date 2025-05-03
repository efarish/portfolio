import logging
import os
from functools import wraps

from dotenv import load_dotenv

load_dotenv() #Need to load environment variables below reference entities.

from entity.user import User, create_user, get_user

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')))

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
    input: dict = info['variables']
    response: User = create_user(**input) 
    return response

@appsync_decorator("Get User")
def get_user_handler(info: dict, /) -> User:
    user_name: str = info['variables'].get('user_name')
    response: User = get_user(user_name) 
    return response

def lambda_handler(event, context):
    logger.debug(f'{event=} {context=}')
    info = event['info']
    match info:
        case {'parentTypeName': 'Mutation', 'fieldName': 'createUser'}:
            response = create_user_handler(info)
            return response                
        case {'parentTypeName': 'Query', 'fieldName': 'getUser'}:
            response = get_user_handler(info)
            return response
        case _:
            raise Exception(f'Unknown operation: {info['parentTypeName']}:{info['fieldName']}')
    