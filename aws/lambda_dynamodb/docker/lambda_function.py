import json
import logging
import os
from functools import wraps

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

from entity.user import User, get_user

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')))

def appsync_decorator(type_name: str):
    def appsync_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> dict:
            info = args[0]
            selectionSetList = info['selectionSetList']
            try:
                result = func(*args, **kwargs)
            except ValueError as ve:
                return {'__typename': 'ErrorResponse','error_type': '400', 'error_message' : f'{ve}'}
            except Exception as e:
                logger.error(f'{e=}')
                return {'__typename': 'ErrorResponse','error_type': '500', 'error_message' : f'Failed to get user'}
            user = result.model_dump()
            response = {key: user[key] for key in selectionSetList} 
            response['__typename'] = type_name               
            return response
        return wrapper
    return appsync_wrapper

@appsync_decorator("User")
def get_user_handler(info: dict, /) -> User:
    user_name = info['variables'].get('user_name')
    response: User = get_user(user_name)
    return response

def lambda_handler(event, context):
    logger.debug(f'{event=} {context=}')
    info = event['info']
    match info:
        case {'parentTypeName': 'Query', 'fieldName': 'getUser'}:
            return get_user_handler(info)
        case _:
            return {'__typename': 'ErrorResponse','error_type': '500', 'error_message' : f'Unknown request.'}
    