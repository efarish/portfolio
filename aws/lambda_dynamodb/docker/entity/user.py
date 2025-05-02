import os
from dataclasses import asdict, dataclass
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from util import auth

USER_TABLE = os.environ.get('USER_TABLE')

@dataclass
class User:
    user_name: str
    role: str
    password: Optional[str]= None

    def model_dump(self):
        return asdict(self)
    
def get_client():
    return boto3.resource('dynamodb')

def create_user(user_name: str, role: str, password: str) -> User:
    client = get_client()
    table = client.Table(USER_TABLE)
    pwd = auth.create_pwd_hash(password).decode('UTF-8')
    user = {"user_name": user_name,"role": role,"password": pwd}
    try:
        table.put_item(Item=user, ConditionExpression='attribute_not_exists(user_name)')
    except ClientError as e:  
        if e.response['Error']['Code']=='ConditionalCheckFailedException':  
            raise ValueError("User already exists") from e
        else: raise
    return User(**user)


def get_user(user_name, return_password=False) -> User:

    client = get_client()
    table = client.Table(USER_TABLE)
    if not return_password:
        response = table.query(KeyConditionExpression=Key("user_name").eq(user_name), 
                               ExpressionAttributeNames={"#user_role":"role"}, ProjectionExpression= 'user_name, #user_role')    
    else:
        response = table.query(KeyConditionExpression=Key("user_name").eq(user_name))
    if response["Count"] == 0:
        raise ValueError("User not found")
    else:
        user = response["Items"][0]
        return User(**user)