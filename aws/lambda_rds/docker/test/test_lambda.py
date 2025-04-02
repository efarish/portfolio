
import os

import lambda_function
from db import engine, get_db
from model import Users
from sqlalchemy import MetaData, delete, select, text


def test_health_check():

    event = {'rawPath': '/health_check'}

    lambda_function.lambda_handler(event, None)

def test_do_select():

    event = {'rawPath': '/do_select'}

    lambda_function.lambda_handler(event, None)

def test_lambda_handler_create_schema():
    event = {"rawPath": "/create_schema"}
    try:
        lambda_function.lambda_handler(event, None)
        for conn in get_db():
            sql = os.getenv('SCHEMA_CHECK')
            statement = select(text(sql))
            result = conn.execute(statement)
            is_found = result.one()[0] 
            assert is_found == True 
    finally:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.drop_all(engine)


def test_lambda_handle_insert_admin_user():
    try:
        event = {"rawPath": "/create_schema"}
        lambda_function.lambda_handler(event, None)
        event = {"rawPath": "/create_admin_user"}
        lambda_function.lambda_handler(event, None)
        for conn in get_db():
            select_statement = select(Users.id, Users.user_name, Users.role).where(Users.user_name == 'admin')
            result = conn.execute(select_statement)
            users = result.all()
            assert len(users) == 1
            user = users[0]
            assert user[1] == 'admin' 
            delete_statement = delete(Users).where(Users.user_name == 'admin')
            result = conn.execute(delete_statement)
            assert result.rowcount == 1
            conn.commit()
        lambda_function.lambda_handler(event, None)
        for conn in get_db():
            insert_statement = select(Users.id, Users.user_name, Users.role).where(Users.user_name == 'admin')
            result = conn.execute(insert_statement)
            users = result.all()
            assert len(users) == 1
    finally:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.drop_all(engine) 

def test_lambda_handle_insert_user_fail_1():
    try:
        event = {"rawPath": "/create_schema"}
        lambda_function.lambda_handler(event, None)
        event = {"rawPath": "/create_user", 'body': '{"role": "user", "password": "a_password"}'}
        result = lambda_function.lambda_handler(event, None)
        assert result['statusCode'] == 400
    finally:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.drop_all(engine)

       
