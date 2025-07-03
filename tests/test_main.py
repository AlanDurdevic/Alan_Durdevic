from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from main import app, get_service
from service import Service
from models import Ticket


@pytest.fixture
def mock_service():
    service = AsyncMock(spec=Service)
    return service


@pytest.fixture
def client(mock_service):
    app.dependency_overrides[get_service] = lambda: mock_service
    with TestClient(app) as client:
        yield client, mock_service
    app.dependency_overrides.clear()


@pytest.fixture
def sample_tickets():
    return [
        Ticket(
            id=1,
            title="Test ticket 1",
            status="open",
            priority="high",
            assignee="testuser1",
        ),
        Ticket(
            id=2,
            title="Test ticket 2",
            status="closed",
            priority="medium",
            assignee="testuser2",
        )
    ]


class TestEndpoints:

    def test_home(self, client: TestClient):
        client, _ = client
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello from TicketHub"}

    def test_get_ticket_ok(self, client: TestClient, sample_tickets):
        test_client, mock_service = client
        mock_service.get_ticket.return_value = sample_tickets[0]

        response = test_client.get("/tickets/1")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Test ticket 1"
        assert data["status"] == "open"
        assert data["priority"] == "high"
        assert data["assignee"] == "testuser1"

    def test_get_ticket_not_found(self, client):
        test_client, mock_service = client
        mock_service.get_ticket.return_value = None

        response = test_client.get("/tickets/999")
        assert response.status_code == 404
