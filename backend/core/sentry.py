"""Sentry integration utilities for FastAPI applications."""

from __future__ import annotations

from typing import Optional
import os


def init_sentry(dsn: Optional[str], app=None, environment: str = "production", release: Optional[str] = None) -> None:
    """Initialize Sentry SDK for FastAPI with optional DSN.

    If DSN is not provided, the function exits gracefully without raising.
    If an ASGI/FastAPI app is supplied, the Sentry ASGI middleware is attached
    to enable request tracing.
    """
    if not dsn:
        return
    try:
        import sentry_sdk  # type: ignore
        from sentry_sdk.integrations.fastapi import FastApiIntegration  # type: ignore
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware  # type: ignore

        # Enable tracing with a reasonable default sample rate. Adjust as needed.
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=0.2,
            integrations=[FastApiIntegration()],
        )

        if app is not None:
            app.add_middleware(SentryAsgiMiddleware)  # type: ignore[arg-type]
    except Exception:
        # Graceful degradation: do not crash the application if Sentry cannot be configured
        return

__all__ = ["init_sentry"]
