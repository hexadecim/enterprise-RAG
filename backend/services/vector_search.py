"""
services/vector_search.py – Tenant-scoped Qdrant vector search.

Every document is stored in Qdrant with a payload field `organization_id`.
All searches MUST include a filter on this field so that users can only
retrieve documents that belong to their own organization.

Flow:
  1. Caller provides a query vector (pre-computed by an embedding model) and
     the user's organization_id (UUID).
  2. This service builds a Qdrant `Filter` that constrains the match to
     documents whose `organization_id` payload equals the caller's org.
  3. The filtered search result is returned as a list of `SearchResult` objects.

No raw Qdrant payloads ever leak across tenant boundaries.
"""

import uuid
from dataclasses import dataclass, field

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import (
    FieldCondition,
    Filter,
    MatchValue,
    ScoredPoint,
)

from backend.config import settings


# ---------------------------------------------------------------------------
# Response dataclass
# ---------------------------------------------------------------------------
@dataclass
class SearchResult:
    """A single document retrieved from Qdrant."""

    point_id: str
    score: float
    # Payload fields from the Qdrant document
    organization_id: str
    document_id: str
    chunk_index: int
    text: str
    metadata: dict = field(default_factory=dict)

    @classmethod
    def from_scored_point(cls, point: ScoredPoint) -> "SearchResult":
        payload = point.payload or {}
        return cls(
            point_id=str(point.id),
            score=point.score,
            organization_id=payload.get("organization_id", ""),
            document_id=payload.get("document_id", ""),
            chunk_index=int(payload.get("chunk_index", 0)),
            text=payload.get("text", ""),
            metadata=payload.get("metadata", {}),
        )


# ---------------------------------------------------------------------------
# Client factory (one shared client per process is fine with AsyncQdrantClient)
# ---------------------------------------------------------------------------
def _make_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        # Add api_key=... here if Qdrant is configured with authentication
    )


# Module-level singleton — reuse across requests
_qdrant_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    """Return the shared AsyncQdrantClient (lazy init)."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = _make_client()
    return _qdrant_client


# ---------------------------------------------------------------------------
# Core search function
# ---------------------------------------------------------------------------
async def search_by_organization(
    query_vector: list[float],
    organization_id: uuid.UUID,
    *,
    collection: str | None = None,
    top_k: int = 5,
    score_threshold: float | None = None,
    extra_filters: list[FieldCondition] | None = None,
) -> list[SearchResult]:
    """
    Perform a vector similarity search scoped strictly to one organization.

    Args:
        query_vector:    Dense embedding of the user's question.
        organization_id: The UUID of the user's Organization.  This is
                         enforced as a **mandatory** payload filter — queries
                         from one tenant can never match documents of another.
        collection:      Qdrant collection name (defaults to settings value).
        top_k:           Maximum number of results to return.
        score_threshold: Only return results above this similarity score.
        extra_filters:   Additional FieldConditions (e.g. document_type filter).

    Returns:
        List of SearchResult, ordered by descending similarity score.

    Raises:
        ValueError: if organization_id is falsy.
        QdrantClientException: propagated from qdrant_client on network errors.
    """
    if not organization_id:
        raise ValueError("organization_id is required for tenant-scoped search.")

    # ── Build the tenant filter ────────────────────────────────────────────
    # The `organization_id` condition is ALWAYS present — it is the
    # multi-tenancy boundary and must never be omitted.
    tenant_condition = FieldCondition(
        key="organization_id",                  # payload key set at ingest time
        match=MatchValue(value=str(organization_id)),
    )

    must_conditions: list[FieldCondition] = [tenant_condition]

    # Optionally append caller-supplied conditions (e.g. file type, date range)
    if extra_filters:
        must_conditions.extend(extra_filters)

    tenant_filter = Filter(must=must_conditions)

    # ── Execute the search ─────────────────────────────────────────────────
    client = get_qdrant_client()
    results: list[ScoredPoint] = await client.search(
        collection_name=collection or settings.QDRANT_COLLECTION,
        query_vector=query_vector,
        query_filter=tenant_filter,
        limit=top_k,
        score_threshold=score_threshold,
        with_payload=True,     # we need the text + metadata back
        with_vectors=False,    # save bandwidth — we don't need the raw vectors
    )

    return [SearchResult.from_scored_point(p) for p in results]


# ---------------------------------------------------------------------------
# Ingest helper (used when storing documents)
# ---------------------------------------------------------------------------
async def upsert_document_chunks(
    collection: str,
    points: list[dict],
) -> None:
    """
    Upsert pre-built Qdrant PointStruct dicts into the collection.

    Each dict must contain:
        - "id"     : str UUID
        - "vector" : list[float]
        - "payload": dict with at minimum { "organization_id": str, ... }

    Callers are responsible for ensuring `organization_id` is always set.
    """
    from qdrant_client.http.models import PointStruct

    client = get_qdrant_client()
    structs = [
        PointStruct(id=p["id"], vector=p["vector"], payload=p["payload"])
        for p in points
    ]
    await client.upsert(collection_name=collection, points=structs)
