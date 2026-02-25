"""JWKS model for authentication keys."""

from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, String, DateTime


class Jwks(SQLModel, table=True):
    """JWKS table for Better Auth keys."""

    __tablename__ = "jwks"

    id: str = Field(primary_key=True)
    public_key: str = Field(sa_column=Column("publicKey", String, nullable=False))
    private_key: str = Field(sa_column=Column("privateKey", String, nullable=False))
    created_at: datetime = Field(sa_column=Column("createdAt", DateTime, nullable=False))