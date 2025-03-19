
import os

import lambda_function
import pytest
from db import engine, get_db
from model import Users
from sqlalchemy import MetaData, delete, select, text


def test_lambda_1():

    lambda_function.lambda_handler(None, None)


def test_lambda_handler_create_schema():
    
    try:
        lambda_function.lambda_handler_create_schema(None, None)
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

def test_lambda_handler_dml():
    try:
        lambda_function.lambda_handler_create_schema(None, None)
        lambda_function.lambda_handler_dml(None, None)
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
        lambda_function.lambda_handler_dml(None, None)
        for conn in get_db():
            insert_statement = select(Users.id, Users.user_name, Users.role).where(Users.user_name == 'A_User')
            result = conn.execute(insert_statement)
            users = result.all()
            assert len(users) == 1
    finally:
        metadata = MetaData()
        metadata.reflect(bind=engine)
        metadata.drop_all(engine)       