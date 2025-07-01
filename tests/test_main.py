from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_tickets():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello from TicketHub"
