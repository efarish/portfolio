import asyncio
import json
import os

from db import Base, engine, get_async_db, get_db
from model import Users
from sqlalchemy import select, text


def do_select(event, context):
    
    print(f'{event=}')

    for conn in get_db():
        statement = select(text("1"))
        result = conn.execute(statement)
        assert result.one()[0] == 1

    return {'statusCode': 200, 'body': f'Done.'}


def create_schema(event, context):
    
    print(f'{event=}')

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

async def insert_user_async(User):
    async for conn in get_async_db():
        user_name = 'A_User'
        create_user_model = Users(
            user_name=user_name,
            role='user',
            password='password')
        conn.add(create_user_model)
        await conn.commit()

LOOP = None

def insert_user(event, context):
    global LOOP 
    if not LOOP:
        LOOP = asyncio.new_event_loop()
        asyncio.set_event_loop(LOOP) 
    LOOP.run_until_complete(insert_user_async(None))
    return {'statusCode': 201, 'body': f'Done.'}


def lambda_handler(event, context):
    print(f'{event=}')
    body = event["body"]
    req = json.loads(body)
    event_type = req['event_type']
    if event_type == 'CREATE_SCHEMA':
        return create_schema(event, context)
    elif event_type == 'DO_SELECT': 
        return do_select(event, context)
    elif event_type == 'INSERT_USER':
        return insert_user(event, context)
    else:
        return {'statusCode': 400, 'body': f'Invalid event type: {event_type}.'}



