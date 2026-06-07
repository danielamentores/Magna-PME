"""Configuracao centralizada da app."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


class Settings(BaseModel):
    app_env: str = Field(default_factory=lambda: os.getenv("APP_ENV", "development"))
    app_secret_key: str = Field(default_factory=lambda: os.getenv("APP_SECRET_KEY", "dev-key"))
    admin_emails: list[str] = Field(
        default_factory=lambda: [
            e.strip() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()
        ]
    )
    supabase_url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_KEY", ""))
    supabase_service_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_KEY", ""))
    google_client_id: str = Field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID", ""))
    google_client_secret: str = Field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET", ""))
    google_redirect_uri: str = Field(
        default_factory=lambda: os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501/oauth/callback")
    )
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    magna_mode: str = Field(default_factory=lambda: os.getenv("MAGNA_MODE", "excel"))
    magna_excel_path: str = Field(default_factory=lambda: os.getenv("MAGNA_EXCEL_PATH", "data/magna_export.xlsx"))
    magna_api_url: str = Field(default_factory=lambda: os.getenv("MAGNA_API_URL", ""))
    magna_api_key: str = Field(default_factory=lambda: os.getenv("MAGNA_API_KEY", ""))

    def require(self, name: str) -> str:
        value = getattr(self, name, "")
        if not value:
            raise RuntimeError(
                f"Configuracao em falta: {name.upper()}. Define-a em .env."
            )
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
