from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EmailMetadata(BaseModel):
    sender: str | None = None
    recipient: str | None = None
    received_at: datetime | None = None
    source: str | None = None
    tags: list[str] = Field(default_factory=list)
    extras: dict[str, Any] = Field(default_factory=dict)


class EmailRequest(BaseModel):
    subject: str = Field(default="", max_length=500)
    body: str = Field(..., min_length=1, max_length=20000)
    metadata: EmailMetadata = Field(default_factory=EmailMetadata)


class BatchEmailRequest(BaseModel):
    emails: list[EmailRequest] = Field(..., min_length=1, max_length=128)


class HighlightSpan(BaseModel):
    token: str
    score: float
    reason: str


class PredictionResponse(BaseModel):
    label: str
    confidence: float
    explanation: str
    risk_score: int
    suspicious_terms: list[HighlightSpan] = Field(default_factory=list)
    retrieved_examples: list[str] = Field(default_factory=list)


class BatchPredictionResponse(BaseModel):
    results: list[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    version: str
    model_loaded: bool
    rag_documents: int


class MetricsResponse(BaseModel):
    total_predictions: int
    label_counts: dict[str, int]
    average_confidence: float
    average_risk_score: float
