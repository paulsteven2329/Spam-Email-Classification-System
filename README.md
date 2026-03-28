# Spam Email Classification System

Enterprise-ready private spam email classification platform with two folders:

- `backend/`: FastAPI + PyTorch + local RAG/explainer pipeline
- `frontend/`: Flutter app for Web + Android

## Architecture

- Flutter client for analysts, administrators, and mobile users
- FastAPI API gateway with JWT-based access tokens
- Transformer-style PyTorch classifier for `ham`, `spam`, and `phishing`
- Local retrieval pipeline seeded from on-prem knowledge examples
- Private explanation generator with no external API calls
- Docker-ready backend deployment for internal hosting

## Quick Start

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/train_classifier.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
flutter pub get
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

Android emulator example:

```bash
flutter run -d android --dart-define=API_BASE_URL=http://10.0.2.2:8000/api/v1
```

## API

- `POST /api/v1/auth/token`
- `POST /api/v1/predict`
- `POST /api/v1/batch_predict`
- `GET /api/v1/health`
- `GET /api/v1/metrics`

## Security Notes

- keep `SPAM_SECRET_KEY` unique per environment
- terminate TLS at ingress or a reverse proxy in production
- restrict `/metrics` to admin roles
- store production tokens using secure platform storage
- tighten CORS before production rollout

## Air-Gapped Notes

- vendor Python wheels and Flutter artifacts internally
- replace seeded RAG data with enterprise-approved examples
- connect a local private LLM adapter later if you run one on-prem
