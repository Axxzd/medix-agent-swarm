from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from .tasks import EndReason


class Citation(BaseModel):
    source_id: str
    source_type: Literal["guideline", "knowledge_base", "web", "case_memory"]
    title: str
    locator: str
    excerpt: str = Field(max_length=300)
    url: str | None = None
    published_date: date | None = None
    retrieved_at: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_quality: Literal["low", "medium", "high"] = "medium"


class ClaimCitationLink(BaseModel):
    claim_id: str
    citation_source_id: str


class InternalFinalResponse(BaseModel):
    answer: str
    risk_level: Literal["low", "medium", "high", "emergency"]
    risk_statement: str
    warnings: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    disclaimer: str
    follow_up: list[str] = Field(default_factory=list)
    end_reason: EndReason
    claim_citation_map: list[ClaimCitationLink] = Field(default_factory=list)


class PublicFinalResponse(BaseModel):
    answer: str
    risk_level: Literal["low", "medium", "high", "emergency"]
    risk_statement: str
    warnings: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    disclaimer: str
    follow_up: list[str] = Field(default_factory=list)
    end_reason: EndReason
