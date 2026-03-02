"""
main.py – FastAPI application entry point.

Routes
------
GET  /          → root info
GET  /health    → liveness probe
POST /query     → tenant-scoped RAG query (vector search)
"""

import time

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import create_all_tables, get_db
from services.vector_search import search_by_organization, SearchResult

import uuid

app = FastAPI(
    title="Enterprise RAG API",
    description="Tenant-scoped Retrieval-Augmented Generation backend.",
    version="0.2.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://frontend:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup – create tables in dev (use Alembic in production)
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup() -> None:
    if settings.APP_ENV == "development":
        await create_all_tables()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str


class QueryRequest(BaseModel):
    """
    Body for POST /query.

    In a real system `query_vector` would be produced by an embedding model
    (e.g. OpenAI text-embedding-3-small) before this call. For now the caller
    supplies the vector directly so the endpoint can be tested independently
    of any particular embedding provider.
    """

    query_vector: list[float] = Field(
        ...,
        description="Dense embedding of the user's question.",
        min_length=1,
    )
    organization_id: uuid.UUID = Field(
        ...,
        description="UUID of the user's Organization — enforces tenant isolation.",
    )
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return.")
    score_threshold: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score (0–1). Results below are excluded.",
    )


class QueryResponse(BaseModel):
    organization_id: uuid.UUID
    results: list[dict]
    total: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Enterprise RAG API is running.",
        "docs": "/docs",
        "version": app.version,
    }


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Liveness probe — always returns 200 if the process is up."""
    return HealthResponse(
        status="ok",
        timestamp=time.time(),
        version=app.version,
    )


@app.post(
    "/query",
    response_model=QueryResponse,
    tags=["RAG"],
    summary="Tenant-scoped vector search",
    description=(
        "Searches the Qdrant collection for documents that are (a) semantically "
        "similar to the query vector AND (b) belong to the caller's organization. "
        "The `organization_id` filter is mandatory — cross-tenant leakage is "
        "structurally impossible."
    ),
)
async def query(
    body: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    """
    Perform a tenant-scoped RAG retrieval.

    The `db` session is injected so that future middleware (e.g. fetching the
    User row, checking quotas, logging queries) can be added without changing
    the signature.
    """
    try:
        results: list[SearchResult] = await search_by_organization(
            query_vector=body.query_vector,
            organization_id=body.organization_id,
            top_k=body.top_k,
            score_threshold=body.score_threshold,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Vector search failed: {exc}",
        )

    return QueryResponse(
        organization_id=body.organization_id,
        results=[
            {
                "point_id": r.point_id,
                "score": r.score,
                "document_id": r.document_id,
                "chunk_index": r.chunk_index,
                "text": r.text,
                "metadata": r.metadata,
            }
            for r in results
        ],
        total=len(results),
    )
