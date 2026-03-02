"""
schemas/organization.py – Pydantic v2 schemas for Organization.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    """Payload accepted when creating a new Organization."""

    name: str = Field(..., min_length=1, max_length=255, example="Acme Corp")
    domain: str = Field(
        ...,
        min_length=3,
        max_length=255,
        pattern=r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        example="acme.com",
        description="Email domain used to auto-assign users (must be unique)",
    )
    description: str | None = Field(None, max_length=2000)


class OrganizationRead(BaseModel):
    """Response schema — never exposes internals."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    domain: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
