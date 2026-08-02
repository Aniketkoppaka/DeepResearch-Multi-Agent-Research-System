from typing import Dict

from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.qdrant import get_qdrant
from app.db.redis import get_redis
from app.db.session import AsyncSessionLocal
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()

@router.get("/healthz", response_model=HealthResponse)
async def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT
    )

@router.get("/readyz", response_model=ReadinessResponse)
async def readinesscheck() -> ReadinessResponse:
    checks: Dict[str, str] = {}
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as e:
        checks["postgres"] = f"error: {str(e)}"
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"
    try:
        qdrant = await get_qdrant()
        await qdrant.get_collections()
        checks["qdrant"] = "ok"
    except Exception as e:
        checks["qdrant"] = f"error: {str(e)}"
    all_ok = all(val == "ok" for val in checks.values())
    return ReadinessResponse(
        status="ok" if all_ok else "degraded",
        checks=checks
    )
