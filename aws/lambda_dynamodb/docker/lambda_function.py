import json
import logging
import os

from dotenv import load_dotenv
from entity import UsersDAO
from pydantic import BaseModel, ValidationError

load_dotenv()

from util import auth

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class CreateUserRequest(BaseModel):
    user_name: str
    password: str
    role: str

class LoginRequest(BaseModel):
    user_name: str
    password: str

class GetUserRequest(BaseModel):
    user_name: str

def health_check():
    return {'statusCode': 200, 'body': 'Service is up!'}

def login(event):
    body = event['body']
    try:
        user = LoginRequest.model_validate_json(body)
        token = auth.login_for_access_token(user.user_name, user.password)
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

def create_user(event):
    body = event['body']
    try:
        user = CreateUserRequest.model_validate_json(body)
        UsersDAO.create_user(**user.model_dump())
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': 'Validation error.'}
    except ValueError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 403, 'body': 'User already exists.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create user.'}
    return {'statusCode': 201, 'body': f'User {user.user_name} added.'}

def get_user(event):
    body = event['body']
    try:
        user = GetUserRequest.model_validate_json(body)
        model_user = UsersDAO.get_user(**user.model_dump())
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': f'Validation error.'}
    except ValueError as ve:
        return {'statusCode': 404, 'body': f'User not found.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create user.'}
    return {'statusCode': 200, 'body': f'{json.dumps(model_user.model_dump())}'}

def lambda_handler(event, context):

    logger.info(f'{event=}')
    logger.info(f'{context=}')
    
    event_type = event['rawPath']
    
    match event_type:
        case '/health_check':
            return health_check()
        case '/login':
            return login(event)
        case '/create_user':
            return create_user(event)
        case '/get_user':
            return get_user(event)
        case _:
            return {'statusCode': 400, 'body': f'Invalid request: {event_type}.'}



