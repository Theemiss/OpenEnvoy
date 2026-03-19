"""Authentication middleware - supports both API key and JWT tokens."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

from ...core.config import settings

logger = logging.getLogger(__name__)

# JWT config (same as auth.py)
JWT_SECRET_KEY = (
    settings.SECRET_KEY.get_secret_value()
    if settings.SECRET_KEY
    else "dev-secret-key-change-in-production"
)
JWT_ALGORITHM = "HS256"


def extract_user_from_token(request: Request) -> dict | None:
    """Extract user info from JWT token in Authorization header."""
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        from jose import jwt

        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {"user_id": int(payload.get("sub")), "email": payload.get("email")}
    except Exception:
        return None


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware - supports API key and JWT tokens."""

    async def dispatch(self, request: Request, call_next):
        """Process request."""
        # Skip auth for public endpoints and auth endpoints
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/metrics",
        ]

        path = request.url.path

        # Skip auth for all auth endpoints
        if path.startswith("/api/v1/auth/"):
            return await call_next(request)

        if path in public_paths:
            return await call_next(request)

        # Check API key
        api_key = request.headers.get("X-API-Key")

        if api_key and api_key == settings.API_KEY.get_secret_value():
            # API key is valid
            request.state.auth_type = "api_key"
            request.state.user_id = None
            return await self._process_request(request, call_next)

        # Check JWT token
        user = extract_user_from_token(request)
        if user:
            request.state.auth_type = "jwt"
            request.state.user_id = user["user_id"]
            request.state.user_email = user["email"]
            return await self._process_request(request, call_next)

        # No valid auth
        logger.warning(f"Unauthorized access attempt to {path}")
        raise HTTPException(status_code=401, detail="Invalid API key or token")

    async def _process_request(self, request: Request, call_next):
        """Process authenticated request."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response
