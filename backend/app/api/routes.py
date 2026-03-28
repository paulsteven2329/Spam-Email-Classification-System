from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import create_access_token, require_role, security_scheme
from app.schemas.email import (
    BatchEmailRequest,
    BatchPredictionResponse,
    EmailRequest,
    HealthResponse,
    MetricsResponse,
    PredictionResponse,
)
from app.services.prediction_service import prediction_service


router = APIRouter()


@router.post("/auth/token")
def issue_token() -> dict[str, str]:
    token = create_access_token(subject="enterprise.user", role="admin")
    return {"access_token": token, "token_type": "bearer"}


@router.post("/predict", response_model=PredictionResponse)
def predict_email(request: EmailRequest) -> PredictionResponse:
    return prediction_service.predict(request)


@router.post("/batch_predict", response_model=BatchPredictionResponse)
def batch_predict(request: BatchEmailRequest) -> BatchPredictionResponse:
    results = [prediction_service.predict(email) for email in request.emails]
    return BatchPredictionResponse(results=results)


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="1.0.0",
        model_loaded=prediction_service.classifier.model_loaded,
        rag_documents=prediction_service.rag.document_count,
    )


@router.get("/metrics", response_model=MetricsResponse)
def metrics(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> MetricsResponse:
    require_role(credentials, {"admin", "auditor"})
    return MetricsResponse(**prediction_service.metrics())
