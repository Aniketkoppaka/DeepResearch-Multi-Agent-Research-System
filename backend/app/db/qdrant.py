from typing import Optional

from qdrant_client import AsyncQdrantClient

from app.core.config import settings

_qdrant_client: Optional[AsyncQdrantClient] = None

async def get_qdrant() -> AsyncQdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _qdrant_client
