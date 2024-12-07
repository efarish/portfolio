import os
import time

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, File, Response, UploadFile

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")

app = FastAPI()

@app.get('/')
def health_check():
    return {'message': 'The container is up.'}

@app.get('/getInfo')
def read_me():
    return {'message': 'Hi from the Upload container v1.'}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    s3 = boto3.client('s3')
    timestr = time.strftime("%Y%m%d_%H%M%S")
    file.filename = f'IMG_{timestr}.png'
    contents = await file.read()
    print(f"File {file.filename} saved at S3 bucket: {S3_BUCKET}")
    s3.put_object(Bucket=S3_BUCKET, Key=file.filename, Body=contents)
    response_json = f'{{"filename":"{file.filename}", "bucket":"{S3_BUCKET}" }}'
    return Response(content=response_json, media_type="application/json")


