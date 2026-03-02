"""
schemas/user.py – Pydantic v2 schemas for User.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload accepted when provisioning (or auto-creating) a User."""

    email: EmailStr
    name: str | None = Field(None, max_length=255)
    avatar_url: str | None = Field(None, max_length=1024)
    provider: str | None = Field(None, max_length=64, example="google")
    organization_id: uuid.UUID


class UserRead(BaseModel):
    """Response schema — safe to return to the client."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str | None
    avatar_url: str | None
    provider: str | None
    organization_id: uuid.UUID
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
