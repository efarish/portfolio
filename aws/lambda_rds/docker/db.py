import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select as select_async
from sqlalchemy.orm import declarative_base, sessionmaker

if os.getenv('DB_URL', ...) is Ellipsis:
    load_dotenv()

DB_URL = os.getenv('DB_URL') 
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DB_URL_ASYNC = os.getenv('DB_URL_ASYNC') 
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
        
