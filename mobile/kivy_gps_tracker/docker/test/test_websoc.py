import json

from db import get_db
from fastapi import status
from model import User_Location
from routers.auth import get_current_user

from .util import *

app.dependency_overrides[get_db] = mock_get_db


def test_connect():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/connect', json={"connectionId": "1"})
    assert response.status_code == status.HTTP_201_CREATED

def test_disconnect():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.post('/websoc/disconnect', json={"connectionId": "1"})
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.parametrize(
    'insert_user',
    ([get_mock_user()]),
    indirect=True
)
def test_update_location(insert_user): 
 
    app.dependency_overrides[get_current_user] = get_mock_user

    user = get_mock_user()

    msg = {'connectionId': '1', 
           'location': json.dumps({'user_name': insert_user.user_name, 'lat': 22.0, 'lng': 22.0 }),
           'callback': 'http://whatever'}

    response = client.post('/websoc/update_location', json=msg)
    assert response.status_code == status.HTTP_200_OK
    
    with TestSessionLocal() as db:
        location_model: User_Location = db.query(User_Location).filter(User_Location.user_id == user.get('id')).first()
        assert  location_model.user_id == user.get('id')
        assert location_model.lat == 22.0
        assert location_model.lng == 22.0

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM user_location'))
        connection.commit()


