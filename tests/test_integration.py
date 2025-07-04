import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_workflow(client):
    # Health check
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "healthy"

    # Root Information
    root_response = client.get("/")
    assert root_response.status_code == 200

    # Individual ticket retrieval
    ticket_response = client.get(f"/tickets/{1}")
    assert ticket_response.status_code == 200

    # All tickets retrieval
    tickets_response = client.get("/tickets?per_page=5")
    assert tickets_response.status_code == 200

    tickets_data = tickets_response.json()
    assert "items" in tickets_data
    assert "total" in tickets_data
    assert tickets_data["per_page"] == 5

    ticket_response = client.get(f"/tickets/{1}")
    assert ticket_response.status_code == 200

    # Search functionality
    search_response = client.get("/tickets/search?q=test")
    assert search_response.status_code == 200

    # Statistics
    stats_response = client.get("/stats")
    assert stats_response.status_code == 200

    stats_data = stats_response.json()
    assert "total_tickets" in stats_data
    assert "priority_breakdown" in stats_data


def test_error_handling(client):
    # Test invalid ticket ID
    invalid_ticket = client.get("/tickets/99999999")
    assert invalid_ticket.status_code == 404

    # Test invalid query parameters
    invalid_status = client.get("/tickets?status=invalid")
    assert invalid_status.status_code == 422

    invalid_priority = client.get("/tickets?priority=invalid")
    assert invalid_priority.status_code == 422
