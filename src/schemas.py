from pydantic import BaseModel
from typing import Literal, Optional, Dict


class User(BaseModel):
    id: int
    username: str


class Ticket(BaseModel):
    id: int
    title: str
    status: Literal["open", "closed"]
    priority: Literal["low", "medium", "high"]
    assignee: Optional[str] = None


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    pages: int


class TicketStats(BaseModel):
    total_tickets: int
    priority_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
