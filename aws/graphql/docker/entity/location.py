import os
from dataclasses import asdict, dataclass, field
from decimal import Decimal

import boto3

USER_LOCATION_TABLE =  os.environ.get('PROJECT_NAME') + '_user_location'

@dataclass
class UserLocation:
    user_name: str
    latitude: str 
    longitude: str 

    def model_dump(self):
        return asdict(self)
    
def get_client():
    return boto3.resource('dynamodb')
    
def update_user_location(user_name: str, latitude: str, longitude: str) -> UserLocation:
    client = get_client()
    table = client.Table(USER_LOCATION_TABLE)
    loc: dict = {"user_name": user_name,"latitude": latitude,"longitude": longitude}
    table.put_item(Item=loc)
    return UserLocation(**loc)

def get_user_locations() -> list[UserLocation]:
    client = get_client()
    table = client.Table(USER_LOCATION_TABLE)
    response = table.scan()    
    if response["Count"] == 0:
        raise ValueError("No locations found.")
    return [UserLocation(**item) for item in response['Items']]