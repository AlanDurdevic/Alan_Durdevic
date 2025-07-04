from pydantic import BaseModel
from typing import Literal, Optional, Dict


class User(BaseModel):
    """User model"""
    id: int
    username: str


class Ticket(BaseModel):
    """Ticket model"""
    id: int
    title: str
    status: Literal["open", "closed"]
    priority: Literal["low", "medium", "high"]
    assignee: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: list
    total: int
    page: int
    per_page: int
    pages: int


class TicketStats(BaseModel):
    """Ticket statistics model"""
    total_tickets: int
    open_tickets: int
    closed_tickets: int
    priority_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
