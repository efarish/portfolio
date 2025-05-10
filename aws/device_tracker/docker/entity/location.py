import os
from dataclasses import asdict, dataclass, field
from decimal import Decimal

import boto3

USER_LOCATION_TABLE =  os.environ.get('PROJECT_NAME') + '_location'

@dataclass
class UserLocation:
    user_name: str
    lat: Decimal = field(metadata={'max_digits': 12, 'decimal_places': 8})
    lon: Decimal = field(metadata={'max_digits': 12, 'decimal_places': 8})

    def model_dump(self):
        return asdict(self)
    
def get_client():
    return boto3.resource('dynamodb')
    
def update_user_location(user_name: str, lat: Decimal, lon: Decimal) -> UserLocation:
    client = get_client()
    table = client.Table(USER_LOCATION_TABLE)
    loc: dict = {"user_name": user_name,"lat": lat,"lon": lon}
    table.put_item(Item=loc)
    return UserLocation(**loc)