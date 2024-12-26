from fastapi import status

from .util import *


def test_read_all(test_admin_user):
    response = client.get('/users/read_all')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [mock_get_current_user()]

