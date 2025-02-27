"""
REST FastAPI for persisting the location history of users.  
"""
from decimal import Decimal
from typing import Annotated, List

from db import get_db
from fastapi import APIRouter, Depends, HTTPException
from model import User_Location, Users
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import Session, aliased
from starlette import status

from .auth import user_dependency

router = APIRouter(
    prefix='/location',
    tags=['location']
)

class UpdateLocationRequest(BaseModel):
    user_name: str
    lat: Decimal = Field(max_digits=12, decimal_places=8)
    lng: Decimal = Field(max_digits=12, decimal_places=8)

class GetUserLocationRequest(BaseModel):
    ids: List[int]

class UserLocations(BaseModel):
    id: int
    user_name: str
    lat: Decimal = Field(max_digits=12, decimal_places=8)
    lng: Decimal = Field(max_digits=12, decimal_places=8)
    
    class Config:
        from_attributes = True


db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/get_locations", status_code=status.HTTP_200_OK, response_model=List[UserLocations])
async def get_user_locations(user: user_dependency, db: db_dependency,
                               get_user_location: GetUserLocationRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    ul = aliased(User_Location)
    statement = select(Users.id, Users.user_name, ul.lat, ul.lng) \
        .join(ul, ul.user_id == Users.id) \
        .filter(Users.id.in_(get_user_location.ids))
    result = await db.execute(statement)
    locs = result.fetchall()
    return locs

@router.post("/update", status_code=status.HTTP_201_CREATED, response_model=List[UserLocations])
async def update_user_location(user: user_dependency, db: db_dependency,
                               update_user_location: UpdateLocationRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_location_model = User_Location(
        user_id=user.get('id'), 
        lat=update_user_location.lat,
        lng=update_user_location.lng
    )
    db.add(user_location_model)
    await db.commit()

    ul = aliased(User_Location)
    cte = select(
        func.max(ul.id).label('max_loc_id'), 
        ul.user_id
    ).group_by(ul.user_id).cte(name='latest_user_locations')
    statement = select(Users.id, Users.user_name, ul.lat, ul.lng) \
        .join(cte, ul.id == cte.c.max_loc_id) \
        .join(Users, Users.id == cte.c.user_id)
    result = await db.execute(statement)
    locs = result.fetchall()
    
    return locs