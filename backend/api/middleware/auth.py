"""Authentication middleware."""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

from ...core.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request."""
        # Skip auth for public endpoints
        public_paths = [
            "/", "/health", "/docs", "/openapi.json", "/redoc",
            "/api/v1/auth/register", "/api/v1/auth/login",
        ]
        
        if request.url.path in public_paths or request.url.path.startswith("/api/v1/auth/"):
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get("X-API-Key")
        
        if not api_key or api_key != settings.API_KEY.get_secret_value():
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        """Process request."""
        # Skip auth for public endpoints
        if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Check API key
        api_key = request.headers.get("X-API-Key")
        
        if not api_key or api_key != settings.API_KEY.get_secret_value():
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response