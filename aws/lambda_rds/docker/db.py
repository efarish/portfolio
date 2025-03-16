import asyncio

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select as select_async
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

#DATABASE_URL =  os.getenv('DATABASE_URL')
DB_DNS = 'database-1.cluster-c4bkhqxdo40l.us-east-1.rds.amazonaws.com'

db_url = f"postgresql+psycopg://testadmin:a_password_@{DB_DNS}:5432/testdb" 
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db_url_async = f"postgresql+asyncpg://testadmin:a_password_@{DB_DNS}:5432/testdb"
engine_async = create_async_engine(db_url_async)
SessionLocal_Async = sessionmaker(bind=engine_async, autocommit=False, autoflush=False, 
                                  expire_on_commit=False, class_=AsyncSession) 

Base = declarative_base()

def get_db():
    with SessionLocal() as session:
        yield session

async def get_async_db():
    async with SessionLocal_Async() as session:
        yield session
        
async def main_async():
    async for conn in get_async_db():
        statement = select_async(text("1"))
        result = await conn.execute(statement)
        assert result.one()[0] == 1


def main():
    for conn in get_db():
        statement = select(text("1"))
        result = conn.execute(statement)
        assert result.one()[0] == 1


if __name__ == '__main__':

    #asyncio.run(main_async())
    main()
