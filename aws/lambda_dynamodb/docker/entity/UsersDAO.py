from dataclasses import asdict, dataclass

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from util import auth

USER_TABLE = "DeviceTracker_User"

@dataclass
class User:
    user_name: str
    role: str
    password: str

    def model_dump(self):
        return asdict(self)
    
def get_client():
    return boto3.client("dynamodb")

def create_user(user_name: str, role: str, password: str) -> User:
    client = get_client()
    table = client.Table(USER_TABLE)
    user = {"user_name": user_name,"role": role,"password":auth.create_pwd_hash('a_password')}
    try:
        table.put_item(Item=user, ConditionExpression='attribute_not_exists(user_name)')
    except ClientError as e:  
        if e.response['Error']['Code']=='ConditionalCheckFailedException':  
            raise ValueError("User already exists") from e
    return User(**user)


def get_user(user_name) -> User:

    client = get_client()
    table = client.Table(USER_TABLE)
    response = table.query(KeyConditionExpression=Key("user_name").eq(user_name))
    if response["Count"] == 0:
        raise ValueError("User not found")
    else:
        return User(**response["Items"][0])