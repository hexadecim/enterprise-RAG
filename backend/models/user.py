"""
models/user.py – User ORM model.

Every User belongs to exactly one Organization (tenant).
The `organization_id` FK is the anchor for all tenant-scoped operations,
including the Qdrant vector search filter.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    # ── Primary key ───────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ── Identity ──────────────────────────────────────────────────────────
    email: Mapped[str] = mapped_column(
        String(320),       # max valid email length per RFC 5321
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Avatar URL from the OAuth provider (optional)
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # OAuth provider used for last login, e.g. "google"
    provider: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ── Tenant FK ─────────────────────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # ── Status / roles ────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship(  # type: ignore[name-defined]
        "Organization",
        back_populates="users",
        lazy="selectin",
    )

    # ── Helpers ───────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} org={self.organization_id}>"
