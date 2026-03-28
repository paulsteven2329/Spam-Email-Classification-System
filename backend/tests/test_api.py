from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_service_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "1.0.0"
    assert isinstance(payload["model_loaded"], bool)
    assert payload["rag_documents"] >= 1


def test_predict_endpoint_returns_valid_prediction() -> None:
    response = client.post(
        "/api/v1/predict",
        json={
            "subject": "Urgent password reset required",
            "body": "Click here to verify your bank account password immediately.",
            "metadata": {"source": "unit_test"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["label"] in {"ham", "spam", "phishing"}
    assert 0.0 <= payload["confidence"] <= 1.0
    assert isinstance(payload["explanation"], str)
    assert 0 <= payload["risk_score"] <= 100
    assert isinstance(payload["suspicious_terms"], list)
    assert isinstance(payload["retrieved_examples"], list)


def test_predict_endpoint_flags_suspicious_terms() -> None:
    response = client.post(
        "/api/v1/predict",
        json={
            "subject": "Verify your bank account",
            "body": "Urgent action needed. Click now and verify your password.",
            "metadata": {},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    tokens = {item["token"] for item in payload["suspicious_terms"]}
    assert {"verify", "password", "bank", "click", "urgent"}.intersection(tokens)


def test_batch_predict_endpoint_returns_multiple_results() -> None:
    response = client.post(
        "/api/v1/batch_predict",
        json={
            "emails": [
                {
                    "subject": "Meeting agenda",
                    "body": "Please review the agenda before tomorrow's sync.",
                    "metadata": {},
                },
                {
                    "subject": "Free gift offer",
                    "body": "You are a winner. Claim your free reward now.",
                    "metadata": {},
                },
            ]
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert "results" in payload
    assert len(payload["results"]) == 2
    for result in payload["results"]:
        assert result["label"] in {"ham", "spam", "phishing"}


def test_metrics_endpoint_requires_authentication() -> None:
    response = client.get("/api/v1/metrics")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing bearer token"


def test_metrics_endpoint_returns_data_with_admin_token() -> None:
    token_response = client.post("/api/v1/auth/token")
    token = token_response.json()["access_token"]

    metrics_response = client.get(
        "/api/v1/metrics",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert metrics_response.status_code == 200
    payload = metrics_response.json()
    assert "total_predictions" in payload
    assert "label_counts" in payload
    assert "average_confidence" in payload
    assert "average_risk_score" in payload
