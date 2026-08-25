import uuid
from pydantic import BaseModel


class ExecutionStartResponse(BaseModel):
    workspace_id: uuid.UUID
    iteration: int
    max_iterations: int
    is_converged: bool
    claims_extracted: int
    status: str
