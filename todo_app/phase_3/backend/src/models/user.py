"""
User model for Phase 3.
Maps to the existing 'user' table created by Better Auth in Phase 2.
Used primarily for read-only access to user details like email.
"""

from sqlmodel import Field, SQLModel
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "user"  # Better Auth default table name

    id: str = Field(primary_key=True)
    email: str
    name: Optional[str] = None
    emailVerified: bool = Field(default=False)
    image: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
