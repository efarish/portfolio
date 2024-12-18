import os

from dotenv import load_dotenv
from fastapi import FastAPI
from routers import auth
from starlette import status

app = FastAPI()

@app.get('/', status_code=status.HTTP_200_OK)
def health_check():
    return {'message': 'The GPS Tracker container is up.'}

