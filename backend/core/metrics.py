"""Prometheus metrics for OpenEnvoy backend.

This module provides lazy-initialized Prometheus metrics using a local
CollectorRegistry to avoid conflicts with the default registry.
It also exposes a small PrometheusMiddleware to collect request metrics.
"""

from __future__ import annotations

from typing import Optional, Callable
import time

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


_REGISTRY: Optional[CollectorRegistry] = None

_JOB_APPLICATIONS_TOTAL: Optional[Counter] = None
_EMAILS_SENT_TOTAL: Optional[Counter] = None
_AI_REQUESTS_TOTAL: Optional[Counter] = None
_AI_REQUEST_DURATION_SECONDS: Optional[Histogram] = None
_QUEUE_SIZE: Optional[Gauge] = None
_HTTP_REQUESTS_TOTAL: Optional[Counter] = None
_HTTP_REQUEST_DURATION_SECONDS: Optional[Histogram] = None


def _get_registry() -> CollectorRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = CollectorRegistry()
    return _REGISTRY


def _get_job_applications_total() -> Counter:
    global _JOB_APPLICATIONS_TOTAL
    if _JOB_APPLICATIONS_TOTAL is None:
        _JOB_APPLICATIONS_TOTAL = Counter(
            "job_applications_total",
            "Total number of job applications processed",
            ["status"],
            registry=_get_registry(),
        )
    return _JOB_APPLICATIONS_TOTAL


def _get_emails_sent_total() -> Counter:
    global _EMAILS_SENT_TOTAL
    if _EMAILS_SENT_TOTAL is None:
        _EMAILS_SENT_TOTAL = Counter(
            "emails_sent_total",
            "Total number of emails sent",
            ["type", "success"],
            registry=_get_registry(),
        )
    return _EMAILS_SENT_TOTAL


def _get_ai_requests_total() -> Counter:
    global _AI_REQUESTS_TOTAL
    if _AI_REQUESTS_TOTAL is None:
        _AI_REQUESTS_TOTAL = Counter(
            "ai_requests_total",
            "Total number of AI provider requests",
            ["provider", "model", "success"],
            registry=_get_registry(),
        )
    return _AI_REQUESTS_TOTAL


def _get_ai_request_duration_seconds() -> Histogram:
    global _AI_REQUEST_DURATION_SECONDS
    if _AI_REQUEST_DURATION_SECONDS is None:
        _AI_REQUEST_DURATION_SECONDS = Histogram(
            "ai_request_duration_seconds",
            "Duration of AI requests in seconds",
            ["provider", "model"],
            registry=_get_registry(),
        )
    return _AI_REQUEST_DURATION_SECONDS


def _get_queue_size() -> Gauge:
    global _QUEUE_SIZE
    if _QUEUE_SIZE is None:
        _QUEUE_SIZE = Gauge(
            "queue_size",
            "Size of various queues",
            ["queue_name"],
            registry=_get_registry(),
        )
    return _QUEUE_SIZE


def _get_http_requests_total() -> Counter:
    global _HTTP_REQUESTS_TOTAL
    if _HTTP_REQUESTS_TOTAL is None:
        _HTTP_REQUESTS_TOTAL = Counter(
            "http_requests_total",
            "Total number of HTTP requests",
            ["method", "path", "status"],
            registry=_get_registry(),
        )
    return _HTTP_REQUESTS_TOTAL


def _get_http_request_duration_seconds() -> Histogram:
    global _HTTP_REQUEST_DURATION_SECONDS
    if _HTTP_REQUEST_DURATION_SECONDS is None:
        _HTTP_REQUEST_DURATION_SECONDS = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "path"],
            registry=_get_registry(),
        )
    return _HTTP_REQUEST_DURATION_SECONDS


def inc_job_applications_total(status: str) -> None:
    _get_job_applications_total().labels(status=status).inc()


def inc_emails_sent_total(type: str, success: bool) -> None:
    _get_emails_sent_total().labels(type=type, success=str(success).lower()).inc()


def inc_ai_requests_total(provider: str, model: str, success: bool) -> None:
    _get_ai_requests_total().labels(provider=provider, model=model, success=str(success).lower()).inc()


def observe_ai_request_duration(provider: str, model: str, duration_seconds: float) -> None:
    _get_ai_request_duration_seconds().labels(provider=provider, model=model).observe(duration_seconds)


def set_queue_size(queue_name: str, size: int) -> None:
    _get_queue_size().labels(queue_name=queue_name).set(size)


def get_metrics() -> str:
    """Return the current metrics in Prometheus exposition format as a string."""
    return generate_latest(_get_registry()).decode("utf-8")


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Starlette/FastAPI middleware to collect basic HTTP metrics.

    - Records total HTTP requests by method/path/status
    - Records request duration per method/path
    All metrics are lazily instantiated and registered in a private registry.
    """

    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        path = request.scope.get("path", "/")
        method = request.method
        status = str(getattr(response, "status_code", 0))

        _get_http_requests_total().labels(method=method, path=path, status=status).inc()
        _get_http_request_duration_seconds().labels(method=method, path=path).observe(duration)
        return response
