import model
from db import engine
from dotenv import load_dotenv
from fastapi import FastAPI
from routers import auth
from starlette import status

load_dotenv()

app = FastAPI()

model.Base.metadata.create_all(bind=engine)

@app.get('/', status_code=status.HTTP_200_OK)
def health_check():
    return {'message': 'The GPS Tracker container is up.'}

