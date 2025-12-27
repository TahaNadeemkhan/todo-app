from fastapi.testclient import TestClient
from todo_app.main import app

client = TestClient(app)

def test_tasks_route_exists():
    # Should return 401 because of missing auth
    response = client.get("/api/user123/tasks")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authorization header missing"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
