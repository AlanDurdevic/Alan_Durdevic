import httpx
from typing import List, Any
from schemas import *
import logging
from aiocache import cached, Cache

logger = logging.getLogger()


class Service:
    """Service for users and tickets"""

    BASE_URL = "https://dummyjson.com"

    def __init__(self):
        self.client = httpx.AsyncClient()

    @cached(ttl=60, cache=Cache.MEMORY)
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
            logger.error(f"Error fetching users: {e}")
            return {}

    @cached(ttl=60, cache=Cache.MEMORY)
    async def fetch_todos(self) -> List[Any]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/todos")
            response.raise_for_status()
            data = response.json()
            return data.get("todos", [])
        except Exception as e:
            logger.error(f"Error fetching todos: {e}")
            return []

    async def transform_todo_to_ticket(self, todo: Dict[str, Any]) -> Ticket:
        users = await self.fetch_users()

        assignee = None
        if todo.get("userId") and todo["userId"] in users:
            user = users[int(todo["userId"])]
            assignee = user.username

        status = "closed" if todo["completed"] is True else "open"
        priority_map = {0: "low", 1: "medium", 2: "high"}
        priority = priority_map[(todo["id"]) % 3]
        return Ticket(id=todo["id"], title=todo["todo"], status=status, priority=priority, assignee=assignee)

    async def get_tickets(self) -> List[Ticket]:
        todos = await self.fetch_todos()
        tickets = []
        for todo in todos:
            try:
                ticket = await self.transform_todo_to_ticket(todo)
                tickets.append(ticket)
            except Exception as e:
                logger.error(f"Error transforming todo: {e}")
                continue

        return tickets

    async def get_ticket(self, ticket_id: id) -> Optional[Ticket]:
        try:
            response = await self.client.get(f"{self.BASE_URL}/todos/{ticket_id}")
            response.raise_for_status()
            todo = response.json()
            return await self.transform_todo_to_ticket(todo)
        except Exception as e:
            logger.error(f"Error fetching ticket {ticket_id}: {e}")
            return None

    async def calculate_stats(self, tickets: List[Ticket]) -> TicketStats:
        total = len(tickets)
        open_count = sum(1 for t in tickets if t.status == "open")
        closed_count = total - open_count

        priority_counts = {"low": 0, "medium": 0, "high": 0}
        for ticket in tickets:
            priority_counts[ticket.priority] += 1

        status_counts = {"open": open_count, "closed": closed_count}

        return TicketStats(
            total_tickets=total,
            priority_breakdown=priority_counts,
            status_breakdown=status_counts
        )
