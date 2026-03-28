from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn


LABELS = ["ham", "spam", "phishing"]

KEYWORD_WEIGHTS = {
    "urgent": 0.18,
    "winner": 0.22,
    "lottery": 0.25,
    "free": 0.14,
    "investment": 0.12,
    "password": 0.28,
    "verify": 0.18,
    "invoice": 0.12,
    "click": 0.16,
    "wire": 0.3,
    "crypto": 0.2,
    "bank": 0.2,
    "account": 0.18,
    "gift": 0.14,
}


class TransformerSpamClassifier(nn.Module):
    def __init__(
        self,
        vocab_size: int = 4096,
        embed_dim: int = 96,
        num_heads: int = 4,
        ff_dim: int = 192,
        num_layers: int = 2,
        num_classes: int = 3,
        max_len: int = 512,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.position_embedding = nn.Embedding(max_len, embed_dim)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=0.1,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(embed_dim, num_classes),
        )
        self.max_len = max_len

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        positions = torch.arange(
            input_ids.size(1), device=input_ids.device
        ).unsqueeze(0)
        hidden = self.embedding(input_ids) + self.position_embedding(positions)
        encoded = self.encoder(hidden)
        pooled = encoded.mean(dim=1)
        return self.classifier(pooled)


@dataclass
class ClassifierResult:
    label: str
    confidence: float
    probabilities: dict[str, float]


class SpamClassifierService:
    def __init__(self, model_path: Path) -> None:
        self.model = TransformerSpamClassifier()
        self.model_path = model_path
        self.model.eval()
        self.model_loaded = False
        if model_path.exists():
            state = torch.load(model_path, map_location="cpu")
            if isinstance(state, dict) and "model_state" in state:
                self.model.load_state_dict(state["model_state"])
                self.model_loaded = True

    def _tokenize(self, text: str) -> torch.Tensor:
        tokens = text.lower().split()
        ids = [abs(hash(token)) % 4095 + 1 for token in tokens[: self.model.max_len]]
        if not ids:
            ids = [0]
        if len(ids) < self.model.max_len:
            ids.extend([0] * (self.model.max_len - len(ids)))
        return torch.tensor([ids], dtype=torch.long)

    def _keyword_bias(self, text: str) -> dict[str, float]:
        lowered = text.lower()
        spam_score = 0.05
        phishing_score = 0.05
        for keyword, weight in KEYWORD_WEIGHTS.items():
            if keyword in lowered:
                spam_score += weight
                if keyword in {"password", "verify", "wire", "bank", "account"}:
                    phishing_score += weight + 0.05
        ham_score = max(0.1, 1.0 - spam_score - phishing_score / 2)
        return {"ham": ham_score, "spam": spam_score, "phishing": phishing_score}

    def predict(self, subject: str, body: str) -> ClassifierResult:
        text = f"{subject}\n{body}".strip()
        keyword_bias = self._keyword_bias(text)

        with torch.no_grad():
            logits = self.model(self._tokenize(text)).squeeze(0)
            probs = torch.softmax(logits, dim=0).tolist()

        combined = {
            label: float((probs[idx] * 0.55) + (keyword_bias[label] * 0.45))
            for idx, label in enumerate(LABELS)
        }
        total = sum(combined.values()) or 1.0
        normalized = {label: score / total for label, score in combined.items()}
        label = max(normalized, key=normalized.get)
        confidence = normalized[label]
        return ClassifierResult(label=label, confidence=confidence, probabilities=normalized)
