import pytest
from src.service import Service
from unittest.mock import MagicMock, patch


@pytest.fixture
def service():
    return Service()


@pytest.fixture
def sample_user_data():
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
def sample_todos():
    return {
        "todos": [
            {
                "id": "1",
                "todo": "Memorize a poem",
                "completed": "false",
                "userId": "100",
            },
            {
                "id": "20",
                "todo": "Watch a documentary",
                "completed": "true",
                "userId": "1",
            }
        ]
    }


class TestService:

    @pytest.mark.asyncio
    async def test_fetch_users(self, service, sample_user_data):
        mock = MagicMock()
        mock.json.return_value = sample_user_data
        mock.raise_for_status.return_value = None

        with patch.object(service.client, 'get', return_value=mock):
            users = await service.fetch_users()

            assert len(users) == 2
            assert users[1].username == "testuser1"
            assert users[2].username == "testuser2"

    @pytest.mark.asyncio
    async def test_fetch_users(self, service, sample_todos):
        mock = MagicMock()
        mock.json.return_value = sample_todos
        mock.raise_for_status.return_value = None

        with patch.object(service.client, 'get', return_value=mock):
            todos = await service.fetch_todos()

            assert len(todos) == 2
            assert todos[0]["id"] == "1"
            assert todos[0]["todo"] == "Memorize a poem"
            assert todos[0]["completed"] == "false"
            assert todos[0]["userId"] == "100"
            assert todos[1]["id"] == "20"
            assert todos[1]["todo"] == "Watch a documentary"
            assert todos[1]["completed"] == "true"
            assert todos[1]["userId"] == "1"
