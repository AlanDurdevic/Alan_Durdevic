import pytest

from models import User
from service import Service
from unittest.mock import MagicMock, patch, AsyncMock


@pytest.fixture
def service():
    return Service()


def _sample_user_data():
    return {
        "users": [
            {
                "id": 1,
                "username": "testuser1",
                "email": "test1@example.com",
                "firstName": "Test",
                "lastName": "User1"
            },
            {
                "id": 2,
                "username": "testuser2",
                "email": "test2@example.com",
                "firstName": "Test",
                "lastName": "User2"
            }
        ]
    }


@pytest.fixture
def sample_user_data():
    return _sample_user_data()


@pytest.fixture
def sample_todo():
    return {
        "id": 1,
        "todo": "Memorize a poem",
        "completed": False,
        "userId": 100,
    }


def _sample_todos():
    return {
        "todos": [
            {
                "id": 1,
                "todo": "Memorize a poem",
                "completed": False,
                "userId": 100,
            },
            {
                "id": 20,
                "todo": "Watch a documentary",
                "completed": True,
                "userId": 1,
            }
        ]
    }


@pytest.fixture
def sample_todos():
    return _sample_todos()


class TestService:

    @pytest.mark.asyncio
    async def test_fetch_users(self, service, sample_user_data):
        mock = MagicMock()
        mock.json.return_value = sample_user_data
        mock.raise_for_status.return_value = None

        with patch.object(service.client, 'get', return_value=mock):
            users = await service.fetch_users()

            assert len(users) == 2

            assert users[1].id == 1
            assert users[1].username == "testuser1"

            assert users[2].id == 2
            assert users[2].username == "testuser2"

    @pytest.mark.asyncio
    async def test_fetch_todos(self, service, sample_todos):
        mock = MagicMock()
        mock.json.return_value = sample_todos
        mock.raise_for_status.return_value = None

        with patch.object(service.client, 'get', return_value=mock):
            todos = await service.fetch_todos()

            assert len(todos) == 2

            assert todos[0]["id"] == 1
            assert todos[0]["todo"] == "Memorize a poem"
            assert todos[0]["completed"] is False
            assert todos[0]["userId"] == 100

            assert todos[1]["id"] == 20
            assert todos[1]["todo"] == "Watch a documentary"
            assert todos[1]["completed"] is True
            assert todos[1]["userId"] == 1

    @pytest.mark.asyncio
    async def test_transform_todo_to_ticket(self, service):
        todos = _sample_todos()
        users_data = _sample_user_data()
        users = {1: User(**users_data["users"][0]), 2: User(**users_data["users"][1])}
        service.fetch_users = AsyncMock(return_value=users)

        first_ticket = await service.transform_todo_to_ticket(todos["todos"][0])
        assert first_ticket.id == 1
        assert first_ticket.title == "Memorize a poem"
        assert first_ticket.status == "open"
        assert first_ticket.priority == "medium"
        assert first_ticket.assignee is None

        second_ticket = await service.transform_todo_to_ticket(todos["todos"][1])
        assert second_ticket.id == 20
        assert second_ticket.title == "Watch a documentary"
        assert second_ticket.status == "closed"
        assert second_ticket.priority == "high"
        assert second_ticket.assignee == "testuser1"

    @pytest.mark.asyncio
    async def test_get_tickets(self, service):
        todos = _sample_todos()["todos"]
        users_data = _sample_user_data()
        users = {1: User(**users_data["users"][0]), 2: User(**users_data["users"][1])}
        service.fetch_todos = AsyncMock(return_value=todos)
        service.fetch_users = AsyncMock(return_value=users)

        tickets = await service.get_tickets()

        first_ticket = tickets[0]
        assert first_ticket.id == 1
        assert first_ticket.title == "Memorize a poem"
        assert first_ticket.status == "open"
        assert first_ticket.priority == "medium"
        assert first_ticket.assignee is None

        second_ticket = tickets[1]
        assert second_ticket.id == 20
        assert second_ticket.title == "Watch a documentary"
        assert second_ticket.status == "closed"
        assert second_ticket.priority == "high"
        assert second_ticket.assignee == "testuser1"

    @pytest.mark.asyncio
    async def test_get_ticket(self, service, sample_todo):
        mock = MagicMock()
        mock.json.return_value = sample_todo
        mock.raise_for_status.return_value = None

        with patch.object(service.client, 'get', return_value=mock):
            ticket = await service.get_ticket(1)

            assert ticket.id == 1
            assert ticket.title == "Memorize a poem"
            assert ticket.status == "open"
            assert ticket.priority == "medium"
            assert ticket.assignee is None
