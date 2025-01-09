from decimal import Decimal

from fastapi import status
from routers.users import get_current_user, get_db

from .util import *

app.dependency_overrides[get_db] = mock_get_db

@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    'insert_user',
    [get_mock_user()],
    indirect=True
)
async def test_update_location(insert_user):
    app.dependency_overrides[get_current_user] = get_mock_user
    mock_user = get_mock_user()
    response = client.post('/location/update', 
                           json={'user_name': mock_user['user_name'], 'lat': 1.0, 'lng': 1.0})
    assert response.status_code == status.HTTP_201_CREATED
    with TestSessionLocal() as db:
        user_loc_model = db.query(User_Location).filter(User_Location.user_id == mock_user['id']).first()
        assert user_loc_model.lat == 1.0
        assert user_loc_model.lng == 1.0 

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM user_location'))
        connection.commit()

@pytest.mark.parametrize(
    'insert_location',
    [{'user': get_mock_user(), 'loc': get_mock_user_location()}],
    indirect=True
)
def test_get_locations(insert_location):
    app.dependency_overrides[get_current_user] = get_mock_user
    mock_loc = get_mock_user_location()
    response = client.post('/location/get_locations', json={'ids': [mock_loc['user_id']]})
    assert response.status_code == status.HTTP_200_OK
    mock_loc = get_mock_user_location()
    response = response.json()[0]
    assert  response['id'] == mock_loc['user_id']
    assert  Decimal(response['lat']) == mock_loc['lat']
    assert  Decimal(response['lng']) == mock_loc['lng']
