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
    """Basic metrics endpoint."""
    from .core.cache import cache
    
    return {
        "queue_sizes": {
            "job_queue": await cache.llen("job_queue"),
            "email_queue": await cache.llen("email_queue"),
            "resume_queue": await cache.llen("resume_queue")
        },
        "timestamp": datetime.now().isoformat()
    }