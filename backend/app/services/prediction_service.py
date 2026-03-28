from __future__ import annotations

from collections import Counter

from app.core.config import get_settings
from app.models.classifier import SpamClassifierService
from app.models.rag_pipeline import RAGPipelineService
from app.schemas.email import EmailRequest, PredictionResponse


class PredictionService:
    def __init__(self) -> None:
        settings = get_settings()
        self.classifier = SpamClassifierService(settings.model_path)
        self.rag = RAGPipelineService(settings.rag_corpus_path)
        self.total_predictions = 0
        self.label_counts: Counter[str] = Counter()
        self.confidence_sum = 0.0
        self.risk_sum = 0

    def predict(self, request: EmailRequest) -> PredictionResponse:
        result = self.classifier.predict(request.subject, request.body)
        explanation, examples, terms = self.rag.explain(
            request.subject,
            request.body,
            result,
        )
        risk_score = round(
            (result.confidence * 70)
            + (25 if result.label == "phishing" else 15 if result.label == "spam" else 5)
            + min(len(terms) * 3, 15)
        )
        self.total_predictions += 1
        self.label_counts[result.label] += 1
        self.confidence_sum += result.confidence
        self.risk_sum += risk_score
        return PredictionResponse(
            label=result.label,
            confidence=round(result.confidence, 4),
            explanation=explanation,
            risk_score=min(risk_score, 100),
            suspicious_terms=terms,
            retrieved_examples=examples,
        )

    def metrics(self) -> dict:
        total = max(self.total_predictions, 1)
        return {
            "total_predictions": self.total_predictions,
            "label_counts": dict(self.label_counts),
            "average_confidence": round(self.confidence_sum / total, 4),
            "average_risk_score": round(self.risk_sum / total, 2),
        }


prediction_service = PredictionService()
