import json
import logging
import os
from dataclasses import asdict

from dotenv import load_dotenv
from entity import UserDAO, UtilDAO
from pydantic import BaseModel, ValidationError

load_dotenv()

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
logger = logging.getLogger(__name__)

class UserRequest(BaseModel):
    user_name: str
    password: str
    role: str

def health_check():
    return {'statusCode': 200, 'body': 'Service is up!'}

def create_schema():
    try:
        UtilDAO.create_schema()
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create schema.'} 

    return {'statusCode': 201, 'body': f'Schema created.'}

def create_admin_user():
    try:
        UserDAO.create_admin_user()
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create admin user.'}

    return {'statusCode': 201, 'body': f'Admin added.'}

def create_user(event):
    body = event['body']
    try:
        user = UserRequest.model_validate_json(body)
        UserDAO.create(**user.model_dump())
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': f'Validation error.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create user.'}
    return {'statusCode': 201, 'body': f'Use {user.user_name} added.'}

def get_users():
    try:
        users = UserDAO.get_users()
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to get all users.'}
    return {'statusCode': 200, 'body': json.dumps([asdict(user) for user in users])}

def lambda_handler(event, context):

    logger.info(f'{event=}')
    logger.info(f'{context=}')
    
    event_type = event['rawPath']
    
    match event_type:
        case '/health_check':
            return health_check()
        case '/create_schema':
            return create_schema()
        case '/create_admin_user':
            return create_admin_user()
        case '/create_user':
            return create_user(event)
        case '/get_users':
            return get_users()
        case _:
            return {'statusCode': 400, 'body': f'Invalid request: {event_type}.'}



