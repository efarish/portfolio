from decimal import Decimal
from typing import Annotated, List

from db import get_db
from fastapi import APIRouter, Depends, HTTPException
from model import User_Location, Users
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, aliased
from starlette import status

from .auth import get_current_user

router = APIRouter(
    prefix='/location',
    tags=['location']
)

class UpdateLocationRequest(BaseModel):
    user_name: str
    lat: Decimal = Field(max_digits=9, decimal_places=6)
    lng: Decimal = Field(max_digits=9, decimal_places=6)

class GetUserLocationRequest(BaseModel):
    ids: List[int]

class UserLocations(BaseModel):
    id: int
    user_name: str
    lat: Decimal = Field(max_digits=9, decimal_places=6)
    lng: Decimal = Field(max_digits=9, decimal_places=6)
    
    class Config:
        from_attributes = True

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.post("/get_locations", status_code=status.HTTP_200_OK, response_model=List[UserLocations])
async def get_user_locations(user: user_dependency, db: db_dependency,
                               get_user_location: GetUserLocationRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    ul = aliased(User_Location)
    
    locs = db.query(Users.id, Users.user_name, ul.lat, ul.lng) \
        .join(ul, ul.user_id == Users.id) \
        .filter(Users.id.in_(get_user_location.ids)).all()
    
    return locs

@router.post("/update", status_code=status.HTTP_201_CREATED)
async def update_user_location(user: user_dependency, db: db_dependency,
                               update_user_location: UpdateLocationRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_location_model = User_Location(
        user_id=user_model.id,
        lat=update_user_location.lat,
        lng=update_user_location.lng
    )
    db.add(user_location_model)
    db.commit()