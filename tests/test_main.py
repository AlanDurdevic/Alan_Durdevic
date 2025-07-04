from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from main import app, Base, get_db
from service import Service
from schemas import Ticket, TicketStats
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

service = AsyncMock(spec=Service)
app.state.service = service


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    return TestClient(app), service


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


class TestHealthAndRootEndpoints:

    def test_health(self, client):
        client, _ = client
        response = client.get("/health")
        assert response.status_code == 200

    def test_hello_message(self, client):
        client, _ = client
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Hello from TicketHub"}


class TestTicketEndpoints:

    def test_get_tickets(self, client, sample_tickets):
        test_client, mock_service = client
        mock_service.get_tickets.return_value = sample_tickets

        response = test_client.get("/tickets")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["per_page"] == 10
        assert len(data["items"]) == 2

        first_ticket = data["items"][0]
        assert first_ticket["id"] == 1
        assert first_ticket["title"] == "Test ticket 1"
        assert first_ticket["status"] == "open"

    def test_get_ticket_ok(self, client, sample_tickets):
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

    def test_search_tickets(self, client, sample_tickets):
        test_client, mock_service = client
        mock_service.get_tickets.return_value = sample_tickets

        response = test_client.get("/tickets/search?q=Test ticket 1")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Test ticket 1"


class TestStatsEndpoints:

    def test_get_stats(self, client, sample_tickets):
        test_client, mock_service = client

        expected_stats = TicketStats(
            total_tickets=2,
            priority_breakdown={"high": 1, "medium": 1, "low": 0},
            status_breakdown={"open": 1, "closed": 1}
        )

        mock_service.get_tickets.return_value = sample_tickets
        mock_service.calculate_stats.return_value = expected_stats

        response = test_client.get("/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["total_tickets"] == 2
        assert data["status_breakdown"]["open"] == 1
        assert data["status_breakdown"]["closed"] == 1
        assert data["priority_breakdown"]["high"] == 1
        assert data["priority_breakdown"]["medium"] == 1
        assert data["priority_breakdown"]["low"] == 0
