from pydantic import BaseModel
from typing import Literal, Optional


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
