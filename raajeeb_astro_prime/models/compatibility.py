"""Models for Ashta Kuta compatibility output."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CompatibilityResult(BaseModel):
    """Ashta Kuta compatibility response."""

    profile_a_id: str
    profile_b_id: str
    total_score_36: float = Field(ge=0, le=36)
    per_kuta_scores: dict[str, float]
    textual_summary: str
