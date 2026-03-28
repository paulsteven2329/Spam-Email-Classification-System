#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
VENV_DIR="$BACKEND_DIR/.venv"

cd "$BACKEND_DIR"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating backend virtual environment..."
  python3 -m venv .venv
fi

source "$VENV_DIR/bin/activate"

if ! python -c "import fastapi, torch" >/dev/null 2>&1; then
  echo "Installing backend dependencies..."
  pip install -r requirements.txt
fi

if [[ ! -f "$BACKEND_DIR/data/models/spam_classifier.pt" ]]; then
  echo "Training initial classifier artifact..."
  python scripts/train_classifier.py
fi

echo "Starting backend on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
