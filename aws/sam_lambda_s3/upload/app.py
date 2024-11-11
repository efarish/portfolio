import base64
import io
import json
import os
import time

import boto3
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET   = os.getenv("S3_BUCKET")
GET_PATH    = '/' + os.getenv("GET_PATH")
POST_PATH   = '/' + os.getenv("POST_PATH")
POST_PATH_2 = '/' + os.getenv("POST_PATH_2")

def detect_labels(imageFile, category_filter=['Plants and Flowers']) -> str:
    session = boto3.Session()
    client = session.client('rekognition')
    s3 = boto3.resource('s3')
    s3_object = s3.Object(S3_BUCKET, imageFile)
    image = s3_object.get()['Body'].read()
    response = client.detect_labels(Image={'Bytes': image},
                                    MaxLabels=5,
                                    MinConfidence=70.0,
                                    Features=["GENERAL_LABELS"],
                                    Settings={"GeneralLabels": {
                                                                "LabelCategoryInclusionFilters": category_filter,
                                                                "LabelExclusionFilters": ['Plant', 'Flower']
                                                                }
                                            }
                                    )
    rek_response = 'Detected labels:'
    for label in response['Labels']:
        rek_response += f"\nLabel: {label['Name']}, Conf: {label['Confidence']:.1f}"
    return rek_response

def deserialize_image(json_string):
    """
    Function used to deserialize POST body that was serialized using json.dumps. The image 
      value was serialized using base64.b64encode. 
    """
    data = json.loads(json_string)
    image_bytes = base64.b64decode(data['image'])
    return io.BytesIO(image_bytes)

def lambda_handler(event, context):
    """
    Lambda event handler. This code assume the API Gateway sends a Payload format version 2, which should be the 
      default format when the `template.yaml` file's  `Type` is set to `HttpApi`.
    """

    if event['rawPath'] == GET_PATH:
        return {
            'statusCode': 200,
            'body': json.dumps('Get info called!')
        }
    elif event['rawPath'] == POST_PATH:
        body = event['body']
        decode_body = base64.b64decode(body)
        s3 = boto3.client('s3')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        key = f'IMG_{timestr}.png'
        s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=decode_body)
        image_labels = detect_labels(key)
        return {'statusCode': 200, 'body': image_labels }
    elif event['rawPath'] == POST_PATH_2:
        body = event['body']
        decode_body = base64.b64decode(body)
        data = deserialize_image(decode_body) 
        print(f'{type(data)=}')
        s3 = boto3.client('s3')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        key = f'IMG_{timestr}.png'
        s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=data.getvalue())        
        return {'statusCode': 200,'body': f'Image uploaded: {key}'}
    else:
        return {'statusCode': 404, 'body': 'Unknown path.'}
