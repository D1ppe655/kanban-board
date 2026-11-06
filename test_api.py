from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_task():
    response = client.post("/tasks", json={"title": "Test Task"})
    assert response.status_code == 200
    assert response.json()["message"] == "Task created"

def test_create_empty_task():
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400