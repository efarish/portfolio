import json
from typing import Annotated, List

import boto3
from db import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from routers.user_location import UpdateLocationRequest, update_user_location
from sqlalchemy.orm import Session
from starlette import status

from .auth import user_dependency

router = APIRouter(
    prefix='/websoc',
    tags=['websoc']
)

class WebSocConnectRequest(BaseModel):
    connectionId: str

class LocationUpdateRequest(BaseModel):
    connectionId: str
    location: str
    callback: str     

CONNECTIONS = {}

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/connect", status_code=status.HTTP_201_CREATED)
async def connect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    
    print(f'User {user.get('id')}:{user.get('user_name')} connected with connection id: {connect_request.connectionId}')
    
    CONNECTIONS[user.get('user_name')] = connect_request.connectionId
    
    print(f'{CONNECTIONS=}')

@router.post("/disconnect", status_code=status.HTTP_201_CREATED)
async def disconnect(connect_request: WebSocConnectRequest):

    print(f'Disconnect called with connection id: {connect_request.connectionId}')
    
    print(f'{CONNECTIONS=}')

    user_connection = [key for key, val in  CONNECTIONS.items() if val == connect_request.connectionId]

    for user in user_connection:
        print(f'Removing user: {user}')
        CONNECTIONS.pop(user)

    print(f'{CONNECTIONS=}')
 

@router.post("/update_location", status_code=status.HTTP_200_OK)
async def update_location(db: db_dependency, update_request: LocationUpdateRequest) -> List[str]:
    """
    Distributes location reported by a user to all other users signed into the app.  
    """
    print(f'Websocket update location: {update_request.connectionId}')

    print(f'{CONNECTIONS=}')
    
    other_connections = [val for key, val in CONNECTIONS.items() if val != update_request.connectionId ]

    print(f'{other_connections=}')

    user_location = json.loads(update_request.location)
    location = UpdateLocationRequest(id=None, user_name=user_location['user_name'], 
                                     lat=user_location['lat'], lng=user_location['lng'])
    await update_user_location(db, location)

    if len(other_connections) > 0: 
        client = boto3.client('apigatewaymanagementapi', endpoint_url=update_request.callback)
        for id in other_connections:
            try:
                response = client.post_to_connection(ConnectionId=id, Data=update_request.location)
                print(f'API GW post response: {response}')
            except Exception as e:
                print(f'Exception on WebSocket callback: {e}')
                CONNECTIONS.pop(id,...) #Assuming connection id is not longer valid, so remove.
        client.close()
    else: print('No connections to broadcast to.')

    return other_connections
   
    
    

