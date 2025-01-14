import functools

from fastapi import status
from model import Users
from routers.auth import get_current_user
from routers.users import get_db

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
    mock_admin = get_mock_admin_user()
    response = response.json()[0]
    assert  response['user_name'] == mock_admin['user_name']
    assert  response['role'] == mock_admin['role']

def test_user_read_all():
    app.dependency_overrides[get_current_user] = get_mock_user
    response = client.get('/users/read_all')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_create():
    request_data={'user_name': 'test_user', 'password': 'password', 'role':'user' }
    response = client.post('/users/create_user', json=request_data)
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

@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    'insert_user',
    ([get_mock_user()]),
    indirect=True
)
async def test_user_update_success(insert_user):
    request_data={'role': 'admin'}
    mock_user = get_mock_user()
    wrap_get_mock_user = functools.partial(get_mock_user, id=mock_user.get('id'))
    app.dependency_overrides[get_current_user] = wrap_get_mock_user
    response = client.put('/users/update', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with TestSessionLocal() as db:
        user_model = db.query(Users).filter(Users.id == mock_user.get('id')).first()
        assert  user_model.role == request_data.get('role')

@pytest.mark.asyncio(loop_scope="function")
@pytest.mark.parametrize(
    'insert_user',
    ([get_mock_user()]),
    indirect=True
)
async def test_user_delete_success(insert_user):
    app.dependency_overrides[get_current_user] = get_mock_admin_user
    mock_user_name = get_mock_user().get('user_name')
    response = client.delete(f'/users/delete/{ mock_user_name }')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    with TestSessionLocal() as db:
        cnt_result = db.query(Users).filter(Users.user_name == mock_user_name).count()
        assert cnt_result == 0

