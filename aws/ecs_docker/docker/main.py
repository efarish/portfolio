import os
import time
import uuid

import boto3
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, Response, UploadFile
from fastapi.responses import JSONResponse

load_dotenv()

IMAGEDIR  = '/app/uploads/'
S3_BUCKET = os.getenv("S3_BUCKET")

app = FastAPI()

@app.get('/')
def health_check():
    return {'message': 'The container is up.'}

@app.get('/getInfo')
def read_me():
    return {'message': 'Hi from the ECS Upload container.'}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    s3 = boto3.client('s3')
    timestr = time.strftime("%Y%m%d_%H%M%S")
    file.filename = f'IMG_{timestr}.png'
    contents = await file.read()
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    print(f"File {file.filename} saved at {IMAGEDIR} and {S3_BUCKET}")
    s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=file.filename, Body=contents)
    s3_file = {"s3_bucket": S3_BUCKET, "s3_imageFile": file.filename}
    
    return s3_file


