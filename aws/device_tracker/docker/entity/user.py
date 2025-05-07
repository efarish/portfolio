import logging
import os
from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from util import auth

USER_TABLE =  os.environ.get('PROJECT_NAME') + '_user'

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'INFO')))

@dataclass
class User:
    user_name: str
    role: str
    password: Optional[str]= None
    def model_dump(self):
        return asdict(self)
    
@dataclass
class UserToken:
    user_name: str
    token: str
    def model_dump(self):
        return asdict(self)
    
def get_client():
    return boto3.resource('dynamodb')

def check_user_name(username: str):
    try:
        user: User = get_user(username,True)
    except ValueError:
        return None
    return user 

def authenticate_user(username: str, password: str):
    user = check_user_name(username) 
    if not user:
        return False
    check = auth.create_pwd_hash(password).decode('UTF-8') == user.password
    if not check:
        return False
    return user

def login_for_access_token(user_name, password):
    """
    Authenticate user, generate and return JWT.
    """
    user = authenticate_user(user_name, password)
    if not user:
        raise ValueError('Could not validate user.')
    token = auth.create_access_token(user.user_name, user.role, timedelta(minutes=1440))
    return UserToken(user.user_name,token)

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

    logger.debug(f"USER_TABLE: {USER_TABLE}")

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