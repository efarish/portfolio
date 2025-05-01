import json
import logging
import os

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

from entity import UsersDAO
from entity.UsersDAO import User
from util.auth import get_current_user, login_for_access_token

log_level_str = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_str)
print(f'{log_level_str=} {log_level=}')
logging.basicConfig(level=log_level)
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


def check_logged_in(event) -> User | None:

    headers = event['headers']
    if('authorization' not in headers):
        print('No Authorization header')
        return None

    user: User | None = None
    try:
        user = get_current_user(headers['authorization'])
    except ValueError as e:
        logger.warning(f'{e=}')
  
    return user


def health_check():
    return {'statusCode': 200, 'body': 'Service is up!'}

def login(event):
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

    user = check_logged_in(event)
    if not user:
        return {'statusCode': 401, 'body': 'Unauthorized.'}

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
        return {'statusCode': 500, 'body': f'Failed to get user.'}
    return {'statusCode': 200, 'body': f'{json.dumps(model_user.model_dump())}'}

def lambda_handler(event, context):


    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Get the effective log level
    effective_level = logger.getEffectiveLevel()
    print(f"Effective log level (using logger.getEffectiveLevel()): {effective_level}")
    level = logger.level
    print(f"log level (using logger.getEffectiveLevel()): {level}")

    logger.info(f'{event=}')
    logger.info(f'{context=}')

    print(f'{event=} {context=}')
    
    event_type = event.get('rawPath',...)
    if event_type is Ellipsis:
        event['info']['parentTypeName']
    
    match event_type:
        case '/health_check':
            return health_check()
        case '/login':
            return login(event)
        case '/create_user':
            return create_user(event)
        case '/get_user':
            return get_user(event)
        case 'Query':
            logger.info(f'{event['info']=}')
            return {'user_name': 'a_user', 'role': 'user', 'password': 'a_password'}
        case _:
            return {'statusCode': 400, 'body': f'Invalid request: {event_type}.'}
