from http import client
from fastapi.testclient import TestClient
from backend.api.app import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "Worlds"}
