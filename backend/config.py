"""
config.py – Application settings loaded from environment variables.

Uses pydantic-settings so every field is validated and type-coerced at startup.
Copy .env.example to .env and fill in real values before running.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Database ─────────────────────────────────────────────────────────────
    # Must be an asyncpg-compatible URL, e.g.:
    #   postgresql+asyncpg://user:password@localhost:5432/enterprise_rag
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/enterprise_rag"

    # Set to True to log all SQL statements (dev only)
    DB_ECHO: bool = False

    # ── Qdrant ───────────────────────────────────────────────────────────────
    QDRANT_HOST: str = "vector-db"   # Docker service name; use "localhost" locally
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "documents"

    # ── Auth ─────────────────────────────────────────────────────────────────
    NEXTAUTH_SECRET: str = "change_me"
    OIDC_CLIENT_ID: str = ""

    # ── FastAPI ──────────────────────────────────────────────────────────────
    APP_ENV: str = "development"   # "production" | "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Single shared instance imported everywhere
settings = Settings()
