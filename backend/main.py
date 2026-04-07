from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .core.config import settings
from .core.sentry import init_sentry
from .core.metrics import PrometheusMiddleware, get_metrics, set_queue_size
import os
from .core.database import db_manager
from .core.cache import cache
from .core.logging import setup_logging
from .api.v1 import api_router
from .core.alerting import alert_manager

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events."""
    # Startup
    logging.info("Starting up...")
    
    # Initialize database
    await db_manager.initialize()
    
    # Initialize cache
    await cache.initialize()
    # Initialize Sentry (graceful if DSN not configured)
    init_sentry(
        dsn=settings.SENTRY_DSN,
        app=app,
        environment=settings.ENVIRONMENT,
        release=os.environ.get("RELEASE"),
    )
    
    # Check health
    health = await alert_manager.check_system_health()
    if health["status"] != "healthy":
        logging.warning(f"System health check: {health}")
        await alert_manager.send_alert(
            title="System Startup",
            message=f"System started with warnings: {health['status']}",
            severity="warning",
            metadata=health
        )
    else:
        await alert_manager.send_alert(
            title="System Started",
            message="Job automation system started successfully",
            severity="info"
        )
    
    yield
    
    # Shutdown
    logging.info("Shutting down...")
    await db_manager.close()
    await cache.close()


# Create FastAPI app
app = FastAPI(
    title="AI Job Automation System",
    version="1.0.0",
    description="AI-Powered Job Application Automation",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrometheusMiddleware)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "AI Job Automation System",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health = await alert_manager.check_system_health()
    return health


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint (text/plain format)."""
    # Update dynamic queue size gauges from cache before exposing metrics
    try:
        job_q = await cache.llen("job_queue")
        email_q = await cache.llen("email_queue")
        resume_q = await cache.llen("resume_queue")
        set_queue_size("job_queue", int(job_q))
        set_queue_size("email_queue", int(email_q))
        set_queue_size("resume_queue", int(resume_q))
    except Exception:
        pass
    from fastapi.responses import Response
    content = get_metrics()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")
