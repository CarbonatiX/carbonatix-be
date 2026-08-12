"""Push AI settings into os.environ for modules that read env at call time."""

from __future__ import annotations

import os

from config import settings


def ensure_ai_env() -> None:
    """Copy Settings into os.environ when set (does not clear existing values)."""
    mapping = {
        "ELICE_API_KEY": settings.ELICE_API_KEY,
        "ELICE_BASE_URL": settings.ELICE_BASE_URL,
        "HELPY_BASE_URL": settings.HELPY_BASE_URL,
        "ELICE_MODEL": settings.ELICE_MODEL,
    }
    for key, value in mapping.items():
        if value:
            os.environ[key] = value


def require_advisor_config() -> None:
    ensure_ai_env()
    missing = [k for k in ("ELICE_API_KEY", "ELICE_BASE_URL") if not os.environ.get(k)]
    if missing:
        raise RuntimeError(
            "Advisor is not configured: " + ", ".join(missing) + " must be set"
        )


def require_ingestion_config() -> None:
    ensure_ai_env()
    missing = [
        k
        for k in ("ELICE_API_KEY", "ELICE_BASE_URL", "HELPY_BASE_URL")
        if not os.environ.get(k)
    ]
    if missing:
        raise RuntimeError(
            "Document ingestion is not configured: "
            + ", ".join(missing)
            + " must be set"
        )
