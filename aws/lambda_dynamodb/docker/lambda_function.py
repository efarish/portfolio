import json
import logging
import os
from dataclasses import asdict

from dotenv import load_dotenv
from entity import UsersDAO
from pydantic import BaseModel, ValidationError

load_dotenv()

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class CreateUserRequest(BaseModel):
    user_name: str
    password: str
    role: str

class GetUserRequest(BaseModel):
    user_name: str
    role: str

def health_check():
    return {'statusCode': 200, 'body': 'Service is up!'}

def create_user(event):
    body = event['body']
    try:
        user = CreateUserRequest.model_validate_json(body)
        UsersDAO.create_user(**user.model_dump())
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': f'Validation error.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create user.'}
    return {'statusCode': 201, 'body': f'Use {user.user_name} added.'}

def get_user(event):
    body = event['body']
    try:
        user = GetUserRequest.model_validate_json(body)
        UsersDAO.create_user(**user.model_dump())
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': f'Validation error.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create user.'}
    return {'statusCode': 201, 'body': f'Use {user.user_name} added.'}

def lambda_handler(event, context):

    logger.info(f'{event=}')
    logger.info(f'{context=}')
    
    event_type = event['rawPath']
    
    match event_type:
        case '/health_check':
            return health_check()
        case '/create_user':
            return create_user(event)
        case '/get_user':
            return get_user(event)
        case _:
            return {'statusCode': 400, 'body': f'Invalid request: {event_type}.'}



