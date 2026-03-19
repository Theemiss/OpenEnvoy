"""Centralized error handling and recovery."""

import logging
import traceback
from typing import Optional, Callable, Any, Dict
import httpx
from functools import wraps
from datetime import datetime

from .alerting import alert_manager
from .database import db_manager

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handler with recovery strategies."""
    
    def __init__(self):
        self.recovery_strategies = {}
        self.error_counts = {}
        self.silent_errors = set()
    
    def register_recovery(self, error_type: type, strategy: Callable):
        """Register a recovery strategy for an error type."""
        self.recovery_strategies[error_type] = strategy
    
    def mark_silent(self, error_type: type):
        """Mark an error type as silent (no alerts)."""
        self.silent_errors.add(error_type)
    
    async def handle_error(self, error: Exception, context: Optional[Dict] = None,
                            component: Optional[str] = None):
        """Handle an error with appropriate strategy."""
        
        error_type = type(error)
        error_key = f"{component}:{error_type.__name__}" if component else error_type.__name__
        
        # Update error count
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error
        logger.error(
            f"Error in {component or 'system'}: {str(error)}\n"
            f"Context: {context}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Send alert unless silent
        if error_type not in self.silent_errors:
            severity = self._determine_severity(error, self.error_counts[error_key])
            
            await alert_manager.send_alert(
                title=f"Error in {component or 'system'}",
                message=str(error),
                severity=severity,
                metadata={
                    "component": component,
                    "error_type": error_type.__name__,
                    "count": self.error_counts[error_key],
                    "context": context
                }
            )
        
        # Apply recovery strategy
        for err_type, strategy in self.recovery_strategies.items():
            if isinstance(error, err_type):
                try:
                    return await strategy(error, context)
                except Exception as e:
                    logger.error(f"Recovery strategy failed: {str(e)}")
        
        return None
    
    def _determine_severity(self, error: Exception, count: int) -> str:
        """Determine alert severity based on error and count."""
        if count > 10:
            return "critical"
        elif count > 5:
            return "error"
        elif count > 2:
            return "warning"
        else:
            return "info"
    
    async def reset_counts(self, component: Optional[str] = None):
        """Reset error counts."""
        if component:
            keys_to_remove = [k for k in self.error_counts if k.startswith(component)]
            for key in keys_to_remove:
                del self.error_counts[key]
        else:
            self.error_counts = {}


class ScraperErrorHandler(ErrorHandler):
    """Specialized error handler for scrapers."""
    
    def __init__(self):
        super().__init__()
        self.setup_recovery_strategies()
    
    def setup_recovery_strategies(self):
        """Setup scraper-specific recovery strategies."""
        
        # Network errors - retry with backoff
        async def handle_network_error(error, context):
            from .scrapers.middleware.rate_limiter import rate_limiter
            
            scraper = context.get("scraper") if context else None
            if scraper:
                # Increase delay for this scraper
                rate_limiter.increase_delay(scraper.source_name)
                
                return {
                    "action": "retry_later",
                    "delay": rate_limiter.get_delay(scraper.source_name)
                }
        
        # Rate limit errors - back off
        async def handle_rate_limit(error, context):
            scraper = context.get("scraper") if context else None
            if scraper:
                return {
                    "action": "rate_limited",
                    "delay": 3600  # Back off for an hour
                }
        
        # Parsing errors - skip and continue
        async def handle_parsing_error(error, context):
            return {
                "action": "skip",
                "reason": "Failed to parse"
            }
        
        self.register_recovery(ConnectionError, handle_network_error)
        self.register_recovery(TimeoutError, handle_network_error)
        self.register_recovery(httpx.HTTPStatusError, handle_rate_limit)
        self.register_recovery(ValueError, handle_parsing_error)
        
        # Mark some errors as silent
        self.mark_silent(ValueError)


# Global error handler instance
error_handler = ErrorHandler()
scraper_error_handler = ScraperErrorHandler()


def with_error_handling(component: Optional[str] = None):
    """Decorator for automatic error handling."""
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                result = await error_handler.handle_error(
                    e, 
                    context=context,
                    component=component or func.__module__
                )
                
                if result is None:
                    raise
                return result
        
        return wrapper
    
    return decorator