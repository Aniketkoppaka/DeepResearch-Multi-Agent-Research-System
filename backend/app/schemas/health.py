from typing import Dict

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

class ReadinessResponse(BaseModel):
    status: str
    checks: Dict[str, str]
