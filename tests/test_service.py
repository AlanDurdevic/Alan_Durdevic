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
