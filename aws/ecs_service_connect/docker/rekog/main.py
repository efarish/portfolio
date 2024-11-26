import os
import time
import uuid

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

@app.get('/')
def health_check():
    return {'message': 'The Rekognition container is up.'}

@app.get('/getInfo')
def read_me():
    return {'message': 'Hi from the ECS Rekognition container.'}

def detect_labels(s3_bucket, s3_imageFile: str, category_filter: list) -> dict:
    session = boto3.Session()
    client = session.client('rekognition')
    s3 = boto3.resource('s3')
    s3_object = s3.Object(s3_bucket, s3_imageFile)
    image = s3_object.get()['Body'].read()
    response = client.detect_labels(Image={'Bytes': image},
                                    MaxLabels=5,
                                    MinConfidence=80.0,
                                    Features=["GENERAL_LABELS"],
                                    Settings={"GeneralLabels": {
                                                                "LabelCategoryInclusionFilters": category_filter,
                                                                "LabelExclusionFilters": ['Plant', 'Flower']
                                                                }
                                            }
                                    )
    rek_response = {}
    for label in response['Labels']:
        rek_response[label['Name']] = f'{label['Confidence']:.1f}'
    return rek_response

class S3File(BaseModel):
    s3_bucket: str
    s3_imageFile: str

@app.post("/get_image_labels")
async def upload_file(s3_file: S3File) -> dict:

    print(f'bucket: {s3_file.s3_bucket}, file: {s3_file.s3_imageFile}')

    image_labels = detect_labels(s3_file.s3_bucket, s3_file.s3_imageFile, category_filter=['Plants and Flowers']) 
    
    return  image_labels

