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

def deserialize_image(json_string):
    """
    Function used to deserialize POST body that was serialized using json.dumps. The image 
      value was serialized using base64.b64encode. An example is below.

    def serialize_image(file_path):
        with open(file_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8') 
        data = {'image': encoded_image}
        json_string = json.dumps(data)
        return json_string

        url = api + '/upload2'
        file_path = "./bkr.png"

        data = serialize_image(file_path)
        response = requests.post(url, data=data)

    """
    data = json.loads(json_string)
    image_bytes = base64.b64decode(data['image'])
    return io.BytesIO(image_bytes)

def lambda_handler(event, context):
    """
    Lambda event handler. This code assume the API Gateway sends a Payload format version 2, which should be default format 
      when the `template.yaml` file's  `Type` is set to `HttpApi`.
    """

    if event['rawPath'] == GET_PATH:
        return {
            'statusCode': 200,
            'body': json.dumps('Get info called!')
        }
    elif event['rawPath'] == POST_PATH:
        #print('ENTER POST')
        body = event['body']
        decode_body = base64.b64decode(body)
        s3 = boto3.client('s3')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        key = f'IMG_{timestr}.png'
        s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=decode_body)
        return {
            'statusCode': 200,
            'body': json.dumps('Post 1 called!')
        }
    elif event['rawPath'] == POST_PATH_2:
        body = event['body']
        decode_body = base64.b64decode(body)
        data = deserialize_image(decode_body) 
        print(f'{type(data)=}')
        s3 = boto3.client('s3')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        key = f'IMG_{timestr}.png'
        s3_upload = s3.put_object(Bucket=S3_BUCKET, Key=key, Body=data.getvalue())        
        return {
            'statusCode': 200,
            'body': json.dumps('Post 2 called!')
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Unknown path.')
        }
