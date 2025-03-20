import json
import os

import boto3
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select as select_async
from sqlalchemy.orm import declarative_base, sessionmaker


def get_db_secrets():

    secret_name = "lambda_rds/secret"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', 
                            region_name=region_name,
                            endpoint_url=f'https://secretsmanager.{region_name}.amazonaws.com')
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    return secret

load_dotenv()

if os.getenv('DB_URL', ...) is Ellipsis:
    secrets = get_db_secrets()
    DB_URL = secrets.get('DB_URL') 
    DB_URL_ASYNC = secrets.get('DB_URL_ASYNC')    
else:
    DB_URL = os.getenv('DB_URL') 
    DB_URL_ASYNC = os.getenv('DB_URL_ASYNC')

print(f'{DB_URL=}')
print(f'{DB_URL_ASYNC=}')

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
engine_async = create_async_engine(DB_URL_ASYNC)
SessionLocal_Async = sessionmaker(bind=engine_async, autocommit=False, autoflush=False, 
                                  expire_on_commit=False, class_=AsyncSession) 

Base = declarative_base()

def get_db():
    with SessionLocal() as session:
        yield session

async def get_async_db():
    async with SessionLocal_Async() as session:
        yield session
        
