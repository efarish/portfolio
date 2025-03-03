from decimal import Decimal

from fastapi import status
from model import User_Location, Users
from routers.auth import get_current_user
from routers.user_location import UpdateLocationRequest, update_user_location
from routers.users import get_db
from sqlalchemy.future import select

from .util import *

app.dependency_overrides[get_db] = mock_get_db

@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    'insert_user',
    [get_mock_user()],
    indirect=True
)
async def test_update_location(insert_user):

    user = insert_user

    async with TestSessionLocal_Async() as db:
        location = UpdateLocationRequest(id=user.id, user_name=user.user_name, lat=0.1, lng=0.2)
        await update_user_location(db=db, location_update=location)
        statement = select(User_Location).where(User_Location.user_id == user.id)
        result = await db.execute(statement)
        user_loc_model = result.one()[0]
        assert user_loc_model.lat == location.lat
        assert user_loc_model.lng == location.lng
    
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM user_location'))
        connection.commit()

@pytest.mark.parametrize(
    'insert_location',
    [{'user': get_mock_user(), 'loc': get_mock_user_location()}],
    indirect=True
)
def test_get_locations(insert_location):
    app.dependency_overrides[get_current_user] = get_mock_admin_user
    mock_loc = get_mock_user_location()
    response = client.get('/location/get_locations')
    assert response.status_code == status.HTTP_200_OK
    mock_loc = get_mock_user_location()
    response = response.json()[0]
    assert  response['id'] == mock_loc['user_id']
    assert  Decimal(response['lat']) == mock_loc['lat']
    assert  Decimal(response['lng']) == mock_loc['lng']



@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    'insert_users',
    [(get_mock_admin_user(), get_mock_user())],
    indirect=True
)
async def test_get_latest_locations(insert_users):
    
    app.dependency_overrides[get_current_user] = get_mock_user

    admin_user = get_mock_admin_user()
    user = get_mock_user()
    
    async with TestSessionLocal_Async() as db:
        admin_location = UpdateLocationRequest(id=admin_user['id'], user_name=admin_user['user_name'], lat=0.0, lng=0.0)
        await update_user_location(db=db, location_update=admin_location)
        location = UpdateLocationRequest(id=user['id'], user_name=user['user_name'], lat=0.1, lng=0.2)
        await update_user_location(db=db, location_update=location)
        location = UpdateLocationRequest(id=user['id'], user_name=user['user_name'], lat=0.3, lng=0.4)
        await update_user_location(db=db, location_update=location)
        response = client.get('/location/get_latest_locations')
        assert response.status_code == status.HTTP_200_OK
        response = response.json()
        assert response[0]['id'] == admin_user['id']
        assert Decimal(response[0]['lat']) == Decimal('0.0') 
        assert response[1]['id'] == user['id']
        assert Decimal(response[1]['lng']) == Decimal('0.4')

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM user_location'))
        connection.commit()
