#import json

from typing import List

import boto3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
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

@router.post("/connect", status_code=status.HTTP_201_CREATED)
async def connect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    
    print(f'User {user.get('id')}:{user.get('user_name')} with websocket connect connection id: {connect_request.connectionId}')
    CONNECTIONS[user.get('user_name')] = connect_request.connectionId
    print(f'{CONNECTIONS=}')

@router.post("/disconnect", status_code=status.HTTP_201_CREATED)
async def disconnect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    print(f'{user.get('id')} websocket disconnect connection id: {connect_request.connectionId}')
    try:
        CONNECTIONS.pop(user.get('user_name'))
        print(f'{CONNECTIONS=}')
    except Exception as e:
        print('Connection Id for user not found.')

@router.post("/get_websocket_ids", status_code=status.HTTP_200_OK)
async def get_websocket_ids(connect_request: LocationUpdateRequest) -> List[str]:
    
    print(f'Websocket update location: {connect_request.connectionId}')

    print(f'{CONNECTIONS=}')
    
    other_connections = [val for key, val in CONNECTIONS.items() if val != connect_request.connectionId ]

    print(f'{other_connections=}')

    if len(other_connections) > 0:
        client = boto3.client('apigatewaymanagementapi', endpoint_url=connect_request.callback) 
        for id in other_connections:
            try:
                response = client.post_to_connection(ConnectionId=id, Data=connect_request.location)
                print(response)
            except Exception as e:
                print(f'Exception on WebSocket callback: {e}')
                CONNECTIONS.pop(id,...) #Assuming connection id is not longer valid, so remove.
        client.close()

    else: print('No connections to broadcast to.')

    return other_connections
   
    
    

