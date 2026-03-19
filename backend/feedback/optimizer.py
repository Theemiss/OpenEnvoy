"""Auto-optimization based on feedback."""

import logging
from typing import Dict, Any, Optional
import json

from .analytics import AnalyticsEngine
from ..core.cache import cache
from ..core.config import settings

logger = logging.getLogger(__name__)


class SystemOptimizer:
    """Automatically optimize system parameters based on feedback."""
    
    def __init__(self):
        self.analytics = AnalyticsEngine()
        self.config_key = "optimizer:config"
    
    async def run_optimization(self) -> Dict[str, Any]:
        """Run optimization cycle."""
        
        logger.info("Starting system optimization cycle")
        
        # Get current config
        current_config = await self._get_current_config()
        
        # Generate insights
        report = await self.analytics.generate_report()
        
        optimizations = []
        
        # Apply optimizations
        for insight in report.get("insights", []):
            if insight["type"] == "threshold_optimization":
                opt = await self._optimize_threshold(insight, current_config)
                if opt:
                    optimizations.append(opt)
            
            elif insight["type"] == "email_optimization":
                opt = await self._optimize_email_patterns(insight, current_config)
                if opt:
                    optimizations.append(opt)
        
        # Save updated config
        if optimizations:
            await self._save_config(current_config)
            logger.info(f"Applied {len(optimizations)} optimizations")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": optimizations,
            "report": report
        }
    
    async def _optimize_threshold(self, insight: Dict, config: Dict) -> Optional[Dict]:
        """Optimize scoring threshold."""
        
        if insight.get("confidence") != "high":
            logger.info("Threshold optimization skipped - confidence not high enough")
            return None
        
        suggested = insight.get("suggested")
        current = insight.get("current")
        
        if suggested and suggested != current:
            # Update config
            config["scoring_threshold"] = suggested
            
            return {
                "type": "threshold_update",
                "parameter": "scoring_threshold",
                "old_value": current,
                "new_value": suggested,
                "reason": insight.get("description")
            }
        
        return None
    
    async def _optimize_email_patterns(self, insight: Dict, config: Dict) -> Optional[Dict]:
        """Optimize email pattern selection."""
        
        best_pattern = insight.get("best_pattern", {}).get("pattern")
        
        if best_pattern:
            # Update email pattern weights
            if "email_pattern_weights" not in config:
                config["email_pattern_weights"] = {}
            
            # Increase weight for best pattern
            old_weight = config["email_pattern_weights"].get(best_pattern, 1.0)
            config["email_pattern_weights"][best_pattern] = old_weight * 1.2
            
            return {
                "type": "email_weight_update",
                "parameter": f"email_pattern_weights.{best_pattern}",
                "old_value": old_weight,
                "new_value": old_weight * 1.2,
                "reason": f"Pattern {best_pattern} shows {insight['best_pattern']['response_rate']}% response rate"
            }
        
        return None
    
    async def _get_current_config(self) -> Dict[str, Any]:
        """Get current system configuration."""
        
        # Try to get from cache
        cached = await cache.get(self.config_key)
        if cached:
            return json.loads(cached)
        
        # Default config
        config = {
            "scoring_threshold": 70,
            "email_pattern_weights": {
                "standard": 1.0,
                "interested": 1.0,
                "casual": 1.0,
                "passionate": 1.0
            },
            "follow_up_days": 5,
            "max_applications_per_day": 10,
            "preferred_sources": ["linkedin", "remotive"]
        }
        
        return config
    
    async def _save_config(self, config: Dict[str, Any]):
        """Save updated configuration."""
        
        await cache.set(self.config_key, json.dumps(config), ttl=0)  # No expiry
        
        # Also update settings in database if needed
        async with db_manager.session() as session:
            from ..models.settings import SystemSetting  # You'd need this model
            
            for key, value in config.items():
                # Update each setting
                pass
    
    async def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get history of optimizations."""
        
        history_key = "optimizer:history"
        history = await cache.lrange(history_key, 0, -1)
        
        return [json.loads(h) for h in history] if history else []