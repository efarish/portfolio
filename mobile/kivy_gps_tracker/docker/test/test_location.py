from decimal import Decimal

from fastapi import status
from model import Users
from routers.users import get_current_user, get_db

from .util import *

app.dependency_overrides[get_db] = mock_get_db


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
