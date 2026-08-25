"""
Canonical State schemas for Multi-Agent Research Execution.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    title: str = Field(..., min_length=1, description="Concise plan title")
    objectives: List[str] = Field(..., min_length=1, description="Core goals of this research")
    research_questions: List[str] = Field(
        ..., min_length=1, description="Granular questions to resolve"
    )
    hypotheses: List[str] = Field(
        default_factory=list, description="Initial hypotheses to validate or disprove"
    )
    search_strategy: Dict[str, Any] = Field(
        default_factory=dict,
        description="Search keywords, domains, and iteration depth parameters",
    )
    expected_sources: List[str] = Field(
        default_factory=list, description="Expected repositories, journals, or data sources"
    )
    deliverables: List[str] = Field(
        default_factory=list, description="Target report sections and outputs"
    )


class AgentExecutionState(BaseModel):
    # State options: idle, planning, pending_approval, executing, completed, failed
    status: str = Field(default="idle")

    current_agent: Optional[str] = None
    progress_percentage: int = Field(default=0, ge=0, le=100)
    current_iteration: int = Field(default=0)
    max_iterations: int = Field(default=3)
    status_messages: List[str] = Field(default_factory=list)
    visited_urls: List[str] = Field(default_factory=list)
    extracted_claim_ids: List[str] = Field(default_factory=list)
