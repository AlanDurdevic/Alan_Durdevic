from pydantic import BaseModel


class User(BaseModel):
    """User model"""
    id: int
    username: str
