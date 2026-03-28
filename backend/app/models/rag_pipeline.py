from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from app.models.classifier import ClassifierResult


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9$@._%-]+")
SUSPICIOUS_TERMS = {
    "urgent": "pressure tactic",
    "verify": "credential harvesting language",
    "password": "credential harvesting language",
    "wire": "fund transfer request",
    "invoice": "unexpected billing lure",
    "gift": "reward enticement",
    "click": "call-to-action link prompt",
    "bank": "financial account targeting",
}


@dataclass
class RetrievedDocument:
    label: str
    subject: str
    body: str
    explanation: str
    similarity: float


class LocalEmbeddingModel:
    def embed(self, text: str) -> dict[str, float]:
        counts: dict[str, float] = {}
        for token in TOKEN_PATTERN.findall(text.lower()):
            counts[token] = counts.get(token, 0.0) + 1.0
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {token: value / norm for token, value in counts.items()}


class LocalVectorStore:
    def __init__(self, corpus_path: Path) -> None:
        self.embedding_model = LocalEmbeddingModel()
        self.documents: list[dict] = []
        if corpus_path.exists():
            self.documents = json.loads(corpus_path.read_text())
        self.embeddings = [
            self.embedding_model.embed(f"{doc['subject']} {doc['body']}")
            for doc in self.documents
        ]

    def similarity_search(self, text: str, top_k: int = 3) -> list[RetrievedDocument]:
        query = self.embedding_model.embed(text)
        scored: list[RetrievedDocument] = []
        for doc, vector in zip(self.documents, self.embeddings, strict=False):
            similarity = sum(query.get(token, 0.0) * weight for token, weight in vector.items())
            scored.append(
                RetrievedDocument(
                    label=doc["label"],
                    subject=doc["subject"],
                    body=doc["body"],
                    explanation=doc["explanation"],
                    similarity=similarity,
                )
            )
        scored.sort(key=lambda item: item.similarity, reverse=True)
        return scored[:top_k]


class PrivateLLMExplainer:
    def generate(
        self,
        subject: str,
        body: str,
        classifier_result: ClassifierResult,
        retrieved_docs: list[RetrievedDocument],
    ) -> str:
        examples = "; ".join(
            f"{doc.label.upper()}: {doc.explanation}" for doc in retrieved_docs[:2]
        )
        base = (
            f"The message was classified as {classifier_result.label.upper()} with "
            f"{classifier_result.confidence:.0%} confidence."
        )
        if classifier_result.label == "phishing":
            rationale = (
                " The content shows credential or payment-seeking behavior that is "
                "common in targeted phishing attempts."
            )
        elif classifier_result.label == "spam":
            rationale = (
                " The content contains promotional or manipulative language often seen "
                "in unsolicited bulk campaigns."
            )
        else:
            rationale = (
                " The message looks operational or conversational and lacks strong scam indicators."
            )
        retrieved = f" Similar internal examples: {examples}." if examples else ""
        return f"{base}{rationale}{retrieved}".strip()


class RAGPipelineService:
    def __init__(self, corpus_path: Path) -> None:
        self.vector_store = LocalVectorStore(corpus_path)
        self.llm = PrivateLLMExplainer()

    @property
    def document_count(self) -> int:
        return len(self.vector_store.documents)

    def suspicious_terms(self, subject: str, body: str) -> list[dict]:
        text = f"{subject} {body}".lower()
        highlights = []
        for token, reason in SUSPICIOUS_TERMS.items():
            if token in text:
                highlights.append(
                    {
                        "token": token,
                        "score": round(0.65 + (len(token) / 20), 2),
                        "reason": reason,
                    }
                )
        return highlights

    def explain(
        self, subject: str, body: str, classifier_result: ClassifierResult
    ) -> tuple[str, list[str], list[dict]]:
        docs = self.vector_store.similarity_search(f"{subject} {body}", top_k=3)
        explanation = self.llm.generate(subject, body, classifier_result, docs)
        examples = [f"{doc.label}: {doc.subject}" for doc in docs]
        return explanation, examples, self.suspicious_terms(subject, body)
