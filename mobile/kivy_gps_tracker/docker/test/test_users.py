from fastapi import status
from model import Users
from routers.users import get_current_user, get_db

from .util import *

app.dependency_overrides[get_db] = mock_get_db

@pytest.mark.parametrize(
    'insert_user',
    ([get_mock_admin_user()]),
    indirect=True
)
def test_admin_read_all(insert_user):
    app.dependency_overrides[get_current_user] = get_mock_admin_user
    response = client.get('/users/read_all')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [get_mock_admin_user()]

def test_user_read_all():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.get('/users/read_all')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_create():
    request_data={'user_name': 'test_user', 'password': 'password', 'role':'user' }
    response = client.post('/users', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    try:
        with TestSessionLocal() as db:
            model = db.query(Users).filter(Users.user_name == request_data['user_name']).first()
            assert model.user_name == request_data.get('user_name')
            assert model.role == request_data.get('role')
            check = bcrypt.checkpw(password=request_data.get('password').encode('UTF-8'), 
                                hashed_password=model.password)
    finally:
        with engine.connect() as connection:
            connection.execute(text('DELETE FROM users'))
            connection.commit()


@pytest.mark.parametrize(
    'insert_user',
    ([get_mock_user()]),
    indirect=True
)
def test_user_update_success(insert_user):
    request_data={'role': 'admin'}
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.put('/users/update', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT

