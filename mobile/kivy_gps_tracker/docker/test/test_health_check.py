from fastapi.testclient import TestClient
import main
from fastapi import status

client = TestClient(main.app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() ==  {'message': 'The GPS Tracker container is up.'}



