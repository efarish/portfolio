import uvicorn
from db import engine
from dotenv import load_dotenv
from fastapi import FastAPI
from model import Base
from routers import auth, user_location, users
from starlette import status

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get('/', status_code=status.HTTP_200_OK)
def health_check():
    return {'message': 'The GPS Tracker container is up.'}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(user_location.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)


