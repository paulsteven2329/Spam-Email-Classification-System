from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "KnightX Shield API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    secret_key: str = Field(default="change-me-enterprise-secret", repr=False)
    access_token_expire_minutes: int = 60
    model_path: Path = BASE_DIR / "data" / "models" / "spam_classifier.pt"
    rag_corpus_path: Path = BASE_DIR / "data" / "rag" / "seed_emails.json"
    max_email_chars: int = 20000
    enable_metrics: bool = True
    tls_required: bool = False
    google_client_id: str = ""
    google_client_secret: str = Field(default="", repr=False)
    google_redirect_uri: str = "http://localhost:3000/inbox"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_prefix="SPAM_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
