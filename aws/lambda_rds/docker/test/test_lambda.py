
import os

import lambda_function
from db import engine, get_db
from sqlalchemy import MetaData, select, text


def test_lambda_1():

    #lambda_function.get_db = mock_get_db

    lambda_function.lambda_handler(None, None)


def test_lambda_handler_create_schema():
    
    lambda_function.lambda_handler_create_schema(None, None)

    for conn in get_db():
        sql = os.getenv('SCHEMA_CHECK')
        statement = select(text(sql))
        result = conn.execute(statement)
        is_found = result.one()[0] 
        assert is_found == True 

    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(engine)