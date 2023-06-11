import unittest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_healthchecker():
    response = client.get("/api/healthchecker")
    assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
