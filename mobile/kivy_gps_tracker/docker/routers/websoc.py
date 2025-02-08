from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status

from .auth import user_dependency

router = APIRouter(
    prefix='/websoc',
    tags=['websoc']
)

class WebSocConnectRequest(BaseModel):
    connectionId: str


@router.post("/connect", status_code=status.HTTP_201_CREATED)
async def connect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    
    print(f'{user.get('id')} websocket connect connection id: {connect_request.connectionId}')

@router.post("/disconnect", status_code=status.HTTP_201_CREATED)
async def disconnect(connect_request: WebSocConnectRequest,
                      user: user_dependency):
    
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    
    print(f'{user.get('id')} websocket disconnect connection id: {connect_request.connectionId}')
    
    


