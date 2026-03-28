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


class GmailAuthUrlResponse(BaseModel):
    auth_url: str
    redirect_uri: str
    scopes: list[str]


class GmailCodeExchangeRequest(BaseModel):
    code: str
    redirect_uri: str | None = None


class GmailTokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    scope: str
    token_type: str
    expires_in: int


class GmailScanRequest(BaseModel):
    access_token: str
    max_results: int = Field(default=10, ge=1, le=25)
    query: str | None = None


class GmailScannedMessage(BaseModel):
    gmail_message_id: str
    thread_id: str
    sender: str
    subject: str
    snippet: str
    received_at: str | None = None
    prediction: PredictionResponse


class GmailScanResponse(BaseModel):
    messages: list[GmailScannedMessage]
    scanned_count: int
    flagged_count: int
