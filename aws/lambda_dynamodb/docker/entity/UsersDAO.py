import boto3
from boto3.dynamodb.conditions import Attr, Key


def add_user(user_name, role, pwd):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("DeviceTracker_Users")
    user = {
        "user_name": user_name,
        "role": role,
        "password":pwd
    }
    table.put_item(Item=user)
    return user


def get_user(user_name):
    dynamodb = boto3.resource("dynamodb")
    #Explicitly specify a region
    #dynamodb = boto3.resource('dynamodb',region_name='us-east-1')
    table = dynamodb.Table("DeviceTracker_Users")

    response = table.query(KeyConditionExpression=Key("user_name").eq(user_name))

    return response["Items"]