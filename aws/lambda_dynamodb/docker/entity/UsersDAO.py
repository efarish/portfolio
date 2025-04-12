import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

USER_TABLE = "DeviceTracker_User"

def create_user(user_name, role, password):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(USER_TABLE)
    user = {"user_name": user_name,"role": role,"password":password}
    try:
        table.put_item(Item=user, ConditionExpression='attribute_not_exists(user_name)')
    except ClientError as e:  
        if e.response['Error']['Code']=='ConditionalCheckFailedException':  
            raise ValueError("User already exists") from e
    return user


def get_user(user_name):
    dynamodb = boto3.resource("dynamodb")
    #Explicitly specify a region
    #dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table(USER_TABLE)

    response = table.query(KeyConditionExpression=Key("user_name").eq(user_name))

    return response["Items"]