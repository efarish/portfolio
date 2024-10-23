import json
import base64
import boto3
import time
import io

GET_PATH = '/getInfo'
POST_PATH = '/upload'
POST_PATH_2 = '/upload2'

def deserialize_image(json_string):
    data = json.loads(json_string)
    image_bytes = base64.b64decode(data['image'])
    return io.BytesIO(image_bytes)

def lambda_handler(event, context):
    print('EVENT')
    #print(event)
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
        s3_upload = s3.put_object(Bucket='rickmartelimagestore', Key=key, Body=decode_body)
        return {
            'statusCode': 200,
            'body': json.dumps('Post 1 called!')
        }
    elif event['rawPath'] == POST_PATH_2:
        body = event['body']
        decode_body = base64.b64decode(body)
        data = deserialize_image(decode_body) 
        print(f'{type(data)=}')
        #print(data)
        s3 = boto3.client('s3')
        timestr = time.strftime("%Y%m%d_%H%M%S")
        key = f'IMG_{timestr}.png'
        s3_upload = s3.put_object(Bucket='rickmartelimagestore', Key=key, Body=data.getvalue())        
        return {
            'statusCode': 200,
            'body': json.dumps('Post 2 called!')
        }
