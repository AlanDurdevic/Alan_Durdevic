import httpx
from typing import Dict, List
from src.models import *


class Service:
    """Service for users and tickets"""

    BASE_URL = "https://dumyjson.com"

    def __init__(self):
        self.client = httpx.AsyncClient()

    async def fetch_users(self) -> Dict[int, User]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/users")
            response.raise_for_status()
            data = response.json()
            users = {}
            for user_data in data.get("users", []):
                user = User(**user_data)
                users[user.id] = user
            return users
        except Exception as e:
            return {}

    async def fetch_todos(self) -> List[any]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/todos")
            response.raise_for_status()
            data = response.json()
            return data.get("todos", [])
        except Exception as e:
            return []
