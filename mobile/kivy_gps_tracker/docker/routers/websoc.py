from decimal import Decimal

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

class UserLocation(BaseModel):
    id: int
    user_name: str
    lat: Decimal = Field(max_digits=12, decimal_places=8)
    lng: Decimal = Field(max_digits=12, decimal_places=8)
    
    class Config:
        from_attributes = True

CONNECTIONS = {}

@router.post("/connect", status_code=status.HTTP_201_CREATED)
async def connect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    
    print(f'User {user.get('id')}:{user.user_name} with websocket connect connection id: {connect_request.connectionId}')
    CONNECTIONS[user.user_name] = connect_request.connectionId

@router.delete("/disconnect", status_code=status.HTTP_201_CREATED)
async def disconnect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    print(f'{user.get('id')} websocket disconnect connection id: {connect_request.connectionId}')
    try:
        CONNECTIONS.pop(user.user_name)
    except Exception as e:
        print('Connection Id for user not found.')

@router.post("/update_location", status_code=status.HTTP_201_CREATED, response_model=UserLocation)
async def get_user_locations(user: user_dependency, user_loc=UserLocation):
    

