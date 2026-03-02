"""
models/organization.py – Organization (tenant) ORM model.

One Organization per tenant.  Every document ingested into Qdrant is tagged
with the organization's `id` so that searches are always tenant-scoped.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Organization(Base):
    __tablename__ = "organizations"

    # ── Primary key ───────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ── Identity ──────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Domain used to auto-assign new users (matches NextAuth tenant_id)
    # e.g. "acme.com"
    domain: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    # Optional: free-form description / plan / tier info
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status ────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    # One organization → many users (lazy="selectin" avoids N+1 on async)
    users: Mapped[list["User"]] = relationship(  # type: ignore[name-defined]
        "User",
        back_populates="organization",
        lazy="selectin",
    )

    # ── Helpers ───────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<Organization id={self.id} domain={self.domain!r}>"
