from fastapi import status

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
    #assert response.status_code == status.HTTP_401_UNAUTHORIZED

