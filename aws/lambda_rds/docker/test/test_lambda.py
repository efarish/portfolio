
import os

import lambda_function
from db import engine, get_db
from model import Users
from sqlalchemy import MetaData, delete, select, text


def test_lambda_1():

    req = {"body":'{"event_type": "DO_SELECT"}'}

    lambda_function.lambda_handler(req, None)


def test_lambda_handler_create_schema():
    req = {"body":'{"event_type": "CREATE_SCHEMA"}'}
    try:
        lambda_function.lambda_handler(req, None)
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

def test_lambda_handle_insert_user():
    try:
        req = {"body":'{"event_type": "CREATE_SCHEMA"}'}
        lambda_function.lambda_handler(req, None)
        req = {"body":'{"event_type": "INSERT_USER"}'}
        lambda_function.lambda_handler(req, None)
        for conn in get_db():
            insert_statement = select(Users.id, Users.user_name, Users.role).where(Users.user_name == 'A_User')
            result = conn.execute(insert_statement)
            users = result.all()
            assert len(users) == 1
            user = users[0]
            assert user[1] == 'A_User' 
            delete_statement = delete(Users).where(Users.user_name == 'A_User')
            result = conn.execute(delete_statement)
            assert result.rowcount == 1
            conn.commit()
        lambda_function.lambda_handler(req, None)
        for conn in get_db():
            insert_statement = select(Users.id, Users.user_name, Users.role).where(Users.user_name == 'A_User')
            result = conn.execute(insert_statement)
            users = result.all()
            assert len(users) == 1
    finally:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.drop_all(engine)       