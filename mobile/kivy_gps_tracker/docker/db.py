import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

#from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, 
                            expire_on_commit=False, class_=AsyncSession) 

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
     
    #try:
    #    yield db
    #finally:
    #    db.close()