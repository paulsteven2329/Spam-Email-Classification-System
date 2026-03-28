from __future__ import annotations

import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.email import EmailMetadata, EmailRequest
from app.services.prediction_service import prediction_service


class GmailService:
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
    SCOPES = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    def __init__(self) -> None:
        self.settings = get_settings()

    def build_auth_url(self, redirect_uri: str | None = None) -> dict[str, Any]:
        if not self.settings.google_client_id:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth client is not configured on the backend",
            )
        callback = redirect_uri or self.settings.google_redirect_uri
        query = urlencode(
            {
                "client_id": self.settings.google_client_id,
                "redirect_uri": callback,
                "response_type": "code",
                "scope": " ".join(self.SCOPES),
                "access_type": "offline",
                "include_granted_scopes": "true",
                "prompt": "consent",
            }
        )
        return {
            "auth_url": f"{self.AUTH_ENDPOINT}?{query}",
            "redirect_uri": callback,
            "scopes": self.SCOPES,
        }

    def exchange_code(self, code: str, redirect_uri: str | None = None) -> dict[str, Any]:
        if not self.settings.google_client_id or not self.settings.google_client_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth client credentials are not configured",
            )
        callback = redirect_uri or self.settings.google_redirect_uri
        payload = {
            "code": code,
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "redirect_uri": callback,
            "grant_type": "authorization_code",
        }
        with httpx.Client(timeout=20.0) as client:
            response = client.post(self.TOKEN_ENDPOINT, data=payload)
        if response.status_code >= 400:
            detail = None
            try:
                detail = response.json().get("error_description")
            except ValueError:
                detail = None
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail or "Failed to exchange Google OAuth code",
            )
        data = response.json()
        return {
            "access_token": data.get("access_token", ""),
            "refresh_token": data.get("refresh_token"),
            "scope": data.get("scope", ""),
            "token_type": data.get("token_type", "Bearer"),
            "expires_in": data.get("expires_in", 0),
        }

    def scan_inbox(
        self, access_token: str, max_results: int = 10, query: str | None = None
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        params: dict[str, Any] = {"maxResults": min(max_results, 25)}
        if query:
            params["q"] = query
        scanned_messages = []
        flagged_count = 0
        with httpx.Client(timeout=20.0) as client:
            response = client.get(
                f"{self.GMAIL_API_BASE}/messages",
                headers=headers,
                params=params,
            )
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch Gmail messages. Check the access token and scopes.",
                )
            message_refs = response.json().get("messages", [])
            for ref in message_refs:
                detail = client.get(
                    f"{self.GMAIL_API_BASE}/messages/{ref['id']}",
                    headers=headers,
                    params={"format": "full"},
                )
                if detail.status_code >= 400:
                    continue
                message = detail.json()
                normalized = self._normalize_message(message)
                prediction = prediction_service.predict(normalized["email_request"])
                if prediction.label in {"spam", "phishing"}:
                    flagged_count += 1
                scanned_messages.append(
                    {
                        "gmail_message_id": message.get("id", ""),
                        "thread_id": message.get("threadId", ""),
                        "sender": normalized["sender"],
                        "subject": normalized["subject"],
                        "snippet": message.get("snippet", ""),
                        "received_at": normalized["received_at"],
                        "prediction": prediction.model_dump(),
                    }
                )
        return {
            "messages": scanned_messages,
            "scanned_count": len(scanned_messages),
            "flagged_count": flagged_count,
        }

    def _normalize_message(self, message: dict[str, Any]) -> dict[str, Any]:
        payload = message.get("payload", {})
        headers = {
            header.get("name", "").lower(): header.get("value", "")
            for header in payload.get("headers", [])
        }
        subject = headers.get("subject", "(No subject)")
        sender = headers.get("from", "Unknown sender")
        received = self._parse_received_at(headers.get("date"))
        body = self._extract_text(payload).strip() or message.get("snippet", "")
        request = EmailRequest(
            subject=subject,
            body=body,
            metadata=EmailMetadata(
                sender=sender,
                received_at=received,
                source="gmail_import",
            ),
        )
        return {
            "subject": subject,
            "sender": sender,
            "received_at": received.isoformat() if received else None,
            "email_request": request,
        }

    def _parse_received_at(self, value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (TypeError, ValueError):
            return None

    def _extract_text(self, payload: dict[str, Any]) -> str:
        mime_type = payload.get("mimeType", "")
        body = payload.get("body", {})
        data = body.get("data")
        if data and mime_type in {"text/plain", "text/html", ""}:
            return self._decode_body(data)
        snippets: list[str] = []
        for part in payload.get("parts", []):
            text = self._extract_text(part)
            if text:
                snippets.append(text)
        return "\n".join(snippets)

    def _decode_body(self, data: str) -> str:
        padded = data + "=" * (-len(data) % 4)
        try:
            decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
            return decoded.decode("utf-8", errors="ignore")
        except (ValueError, UnicodeDecodeError):
            return ""


gmail_service = GmailService()
