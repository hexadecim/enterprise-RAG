"""
models/__init__.py

Re-exports all ORM models so that `import models` registers
every model's metadata with Base — required by create_all_tables().
"""

from models.organization import Organization  # noqa: F401
from models.user import User  # noqa: F401

__all__ = ["Organization", "User"]
