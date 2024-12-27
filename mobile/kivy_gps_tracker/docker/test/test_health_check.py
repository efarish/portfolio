from fastapi import status

from .util import *


def test_read_main():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() ==  {'message': 'The GPS Tracker container is up.'}



