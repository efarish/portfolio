from contextlib import asynccontextmanager

import uvicorn
from db import SessionLocal, engine
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from model import Base
from routers import auth, user_location, users
from starlette import status

load_dotenv()

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before app starts
    await create_db_and_tables()
    try:
        a_user = users.CreateUserRequest(user_name='admin', password='a_password_', role='admin')
        async with SessionLocal() as db:
            await users.create_user_util(db, a_user)
    except HTTPException as e:
        #If status is code is 401, admin user already exists. And thats okay.
        #  Otherwise, re-throw exception.
        if e.status_code != 401: 
            raise e 
    try:
        yield
    finally:
        # After the app stops
        await engine.dispose()

app = FastAPI(
    title='TBD Web API',
    description='Lets just wait and see what this becomes.',    
    lifespan=lifespan)

@app.get('/', status_code=status.HTTP_200_OK)
def health_check():
    return {'message': 'The GPS Tracker container is up.'}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(user_location.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)


