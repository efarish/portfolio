import asyncio
import os

from db import Base, engine, get_async_db, get_db
from model import User_Location, Users
from sqlalchemy import select, text


def lambda_handler(event, context):
    
    print(f'{event=}')

    for conn in get_db():
        statement = select(text("1"))
        result = conn.execute(statement)
        assert result.one()[0] == 1

    return {'statusCode': 200, 'body': f'Done.'}


def lambda_handler_create_schema(event, context):
    
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

async def insert_user(User):
    
    async for conn in get_async_db():
        user_name = 'A_User'
        create_user_model = Users(
            user_name=user_name,
            role='user',
            password='password')
        conn.add(create_user_model)
        await conn.commit()

LOOP = None

def lambda_handler_dml(event, context):
    global LOOP 
    if not LOOP:
        LOOP = asyncio.new_event_loop()
        asyncio.set_event_loop(LOOP) 
    LOOP.run_until_complete(insert_user(None))
    return {'statusCode': 201, 'body': f'Done.'}


