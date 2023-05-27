from fastapi.testclient import TestClient

from backend.apps.api.main import app

client = TestClient(app)


def test_read_root():
    assert True
