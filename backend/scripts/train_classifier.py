from __future__ import annotations

from pathlib import Path
import sys

import torch
from torch import nn
from torch.optim import AdamW

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.classifier import LABELS, TransformerSpamClassifier


SAMPLES = [
    ("Team meeting reminder", "Please join the finance sync at 10am.", "ham"),
    ("Invoice attached", "Monthly invoice for approved services.", "ham"),
    ("You are a winner", "Claim your free gift card now.", "spam"),
    ("Cheap crypto opportunity", "Double your investment today.", "spam"),
    ("Verify your password", "Click here to keep your bank account active.", "phishing"),
    ("Urgent wire request", "Transfer funds to the updated beneficiary today.", "phishing"),
]


def tokenize(text: str, max_len: int = 512) -> torch.Tensor:
    tokens = text.lower().split()
    ids = [abs(hash(token)) % 4095 + 1 for token in tokens[:max_len]]
    if len(ids) < max_len:
        ids.extend([0] * (max_len - len(ids)))
    return torch.tensor(ids, dtype=torch.long)


def train(output_path: Path) -> None:
    model = TransformerSpamClassifier()
    optimizer = AdamW(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    inputs = torch.stack([tokenize(f"{subject} {body}") for subject, body, _ in SAMPLES])
    labels = torch.tensor([LABELS.index(label) for _, _, label in SAMPLES], dtype=torch.long)

    model.train()
    for _ in range(40):
        optimizer.zero_grad()
        logits = model(inputs)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state": model.state_dict()}, output_path)
    print(f"Saved model to {output_path}")


if __name__ == "__main__":
    train(PROJECT_ROOT / "data" / "models" / "spam_classifier.pt")
