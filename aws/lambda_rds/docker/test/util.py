
from db import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite connection for test suite.
DB_URL = 'sqlite:///./testdb.db'
engine = create_engine(DB_URL,connect_args={"check_same_thread": False}, poolclass=StaticPool,)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Mock SQLite connection for application code. 
DB_URL_ASYNC = 'sqlite+aiosqlite:///./testdb.db'
engine_async = create_async_engine(DB_URL_ASYNC, connect_args={'check_same_thread': False}, poolclass=StaticPool,)
TestSessionLocal_Async= sessionmaker(bind=engine_async, autocommit=False, autoflush=False, 
                                     expire_on_commit=False, class_=AsyncSession) 

def mock_get_db():
    with TestSessionLocal() as session:
        yield session

async def mock_get_async_db():
    async with TestSessionLocal_Async() as session:
        yield session

