import json
import logging
import os

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
    print(f'body=')
    try:
        user = UserRequest.model_validate_json(body)
        UserDAO.create(user.user_name, user.role, user.password)
    except ValidationError as ve:
        logger.error(f'{ve=}')
        return {'statusCode': 400, 'body': f'Validation error.'}
    except Exception as e:
        logger.error(f'{e=}')
        return {'statusCode': 500, 'body': f'Failed to create user.'}
    return {'statusCode': 201, 'body': f'Use {user.user_name} added.'}

def lambda_handler(event, context):

    print(f'{event=}')
    print(f'{context=}')
    
    #body = json.loads(event["body"])
    #print(f'body=')

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
        case _:
            return {'statusCode': 400, 'body': f'Invalid request: {event_type}.'}



