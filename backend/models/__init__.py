"""
models/__init__.py

Re-exports all ORM models so that `import backend.models` registers
every model's metadata with Base — required by create_all_tables().
"""

from backend.models.organization import Organization  # noqa: F401
from backend.models.user import User  # noqa: F401

__all__ = ["Organization", "User"]
