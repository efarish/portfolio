import json
import os

from db import Base, engine, get_async_db, get_db
from model import Users
from pydantic import BaseModel, ValidationError
from sqlalchemy import select, text


class UserRequest(BaseModel):
    user_name: str
    password: str
    role: str

def health_check():
    return {'statusCode': 200, 'body': 'Service is up!'}

def do_select():

    for conn in get_db():
        statement = select(text("1"))
        result = conn.execute(statement)
        assert result.one()[0] == 1

    return {'statusCode': 200, 'body': 'Done.'}


def create_schema():

    for conn in get_db():
        sql = os.getenv('SCHEMA_CHECK')
        statement = select(text(sql))
        result = conn.execute(statement)
        is_found = result.one()[0] 
        if not is_found:
            print(f'Creating schema...')
            Base.metadata.create_all(bind=engine)
        else: print(f'Schema already exists.')
    
    return {'statusCode': 201, 'body': f'Done.'}

def create_admin_user():
    for conn in get_db():
        create_user_model = Users(
            user_name='admin',
            role='admin',
            password='a_password_')
        conn.add(create_user_model)
        conn.commit()
    return {'statusCode': 201, 'body': f'Admin added.'}

def create_user(event):
    body = event['body']
    print(f'body=')
    try:
        user = UserRequest.model_validate_json(body)
    except ValidationError as ve:
        print(f've=')
        return {'statusCode': 400, 'body': f'Failed to create user.'}
    for conn in get_db():
        create_user_model = Users(
            user_name=user.user_name,
            role=user.role,
            password=user.password)
        conn.add(create_user_model)
        conn.commit()
    return {'statusCode': 201, 'body': f'Use {user.user_name} added.'}

def lambda_handler(event, context):

    print(f'{event=}')
    print(f'{context=}')
    
    #body = json.loads(event["body"])
    #print(f'body=')

    event_type = event['rawPath']
    
    match event_type:
        case '/health':
            return health_check()
        case '/create_schema':
            return create_schema()
        case '/do_select': 
            return do_select()
        case '/create_admin_user':
            return create_admin_user()
        case '/create_user':
            return create_user(event)
        case _:
            return {'statusCode': 400, 'body': f'Invalid request: {event_type}.'}



