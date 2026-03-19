"""AI cost tracking and monitoring."""

import json
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field

from ..core.cache import cache
from ..core.database import db_manager

logger = logging.getLogger(__name__)


@dataclass
class AICallRecord:
    """Record of an AI API call."""
    
    timestamp: datetime
    model: str
    operation: str  # scoring, resume_adaptation, email_drafting, classification
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    latency: float
    job_id: Optional[int] = None
    success: bool = True
    error: Optional[str] = None


class AICostTracker:
    """Track and analyze AI API costs."""
    
    def __init__(self):
        self.daily_costs = defaultdict(float)
        self.weekly_costs = defaultdict(float)
        self.monthly_costs = defaultdict(float)
        self.operation_counts = defaultdict(int)
        
        # Redis keys
        self.cost_key = "ai:costs:daily"
        self.history_key = "ai:history"
    
    async def record_call(self, record: AICallRecord):
        """Record an AI API call."""
        
        # Update in-memory counters
        date_str = record.timestamp.date().isoformat()
        week_str = f"{record.timestamp.year}-W{record.timestamp.isocalendar()[1]}"
        month_str = record.timestamp.strftime("%Y-%m")
        
        self.daily_costs[date_str] += record.cost
        self.weekly_costs[week_str] += record.cost
        self.monthly_costs[month_str] += record.cost
        self.operation_counts[record.operation] += 1
        
        # Store in Redis for persistence
        await self._store_record(record)
        
        # Update daily total in Redis
        await cache.hincrbyfloat(
            self.cost_key,
            date_str,
            record.cost
        )
        
        # Log for debugging
        logger.info(
            f"AI Call - {record.operation} | Model: {record.model} | "
            f"Tokens: {record.total_tokens} | Cost: ${record.cost:.6f} | "
            f"Latency: {record.latency:.2f}s"
        )
    
    async def _store_record(self, record: AICallRecord):
        """Store record in Redis list."""
        record_dict = {
            "timestamp": record.timestamp.isoformat(),
            "model": record.model,
            "operation": record.operation,
            "prompt_tokens": record.prompt_tokens,
            "completion_tokens": record.completion_tokens,
            "total_tokens": record.total_tokens,
            "cost": record.cost,
            "latency": record.latency,
            "job_id": record.job_id,
            "success": record.success
        }
        
        # Add to history list, keep last 1000 records
        await cache.lpush(self.history_key, json.dumps(record_dict))
        await cache.ltrim(self.history_key, 0, 999)
    
    async def get_daily_costs(self, days: int = 30) -> Dict[str, float]:
        """Get daily costs for the last N days."""
        costs = await cache.hgetall(self.cost_key)
        
        # Filter and sort
        today = date.today()
        result = {}
        
        for date_str, cost in costs.items():
            try:
                record_date = date.fromisoformat(date_str)
                if (today - record_date).days <= days:
                    result[date_str] = float(cost)
            except:
                continue
        
        return dict(sorted(result.items()))
    
    async def get_operation_breakdown(self, days: int = 7) -> Dict[str, Any]:
        """Get cost breakdown by operation for last N days."""
        records = await self.get_recent_records(days)
        
        breakdown = {
            "scoring": {"count": 0, "cost": 0, "tokens": 0},
            "resume_adaptation": {"count": 0, "cost": 0, "tokens": 0},
            "email_drafting": {"count": 0, "cost": 0, "tokens": 0},
            "classification": {"count": 0, "cost": 0, "tokens": 0},
            "other": {"count": 0, "cost": 0, "tokens": 0}
        }
        
        for record in records:
            op = record["operation"]
            if op not in breakdown:
                op = "other"
            
            breakdown[op]["count"] += 1
            breakdown[op]["cost"] += record["cost"]
            breakdown[op]["tokens"] += record["total_tokens"]
        
        # Round costs
        for op in breakdown:
            breakdown[op]["cost"] = round(breakdown[op]["cost"], 4)
        
        return breakdown
    
    async def get_recent_records(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent AI call records."""
        records = await cache.lrange(self.history_key, 0, 999)
        
        cutoff = datetime.now() - timedelta(days=days)
        result = []
        
        for record_str in records:
            try:
                record = json.loads(record_str)
                record_time = datetime.fromisoformat(record["timestamp"])
                
                if record_time >= cutoff:
                    result.append(record)
            except:
                continue
        
        return result
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get cost summary."""
        daily = await self.get_daily_costs(30)
        breakdown = await self.get_operation_breakdown(7)
        
        total_cost_30d = sum(daily.values())
        total_cost_7d = sum(v for d, v in daily.items() 
                           if (date.today() - date.fromisoformat(d)).days <= 7)
        
        # Get average cost per operation
        avg_costs = {}
        for op, data in breakdown.items():
            if data["count"] > 0:
                avg_costs[op] = round(data["cost"] / data["count"], 6)
        
        return {
            "period": {
                "last_7_days": round(total_cost_7d, 4),
                "last_30_days": round(total_cost_30d, 4),
                "daily_average": round(total_cost_30d / 30, 4) if total_cost_30d > 0 else 0
            },
            "breakdown": breakdown,
            "average_cost_per_call": avg_costs,
            "total_calls": sum(data["count"] for data in breakdown.values())
        }
    
    async def get_job_costs(self, job_id: int) -> List[Dict[str, Any]]:
        """Get all AI costs associated with a specific job."""
        records = await self.get_recent_records(90)  # Last 90 days
        
        job_records = [r for r in records if r.get("job_id") == job_id]
        
        total_cost = sum(r["cost"] for r in job_records)
        operations = [r["operation"] for r in job_records]
        
        return {
            "job_id": job_id,
            "total_cost": round(total_cost, 4),
            "call_count": len(job_records),
            "operations": list(set(operations)),
            "records": job_records
        }
    
    async def reset_daily_counter(self):
        """Reset daily counter (call at start of each day)."""
        # Archive old data if needed
        yesterday = date.today() - timedelta(days=1)
        yesterday_str = yesterday.isoformat()
        
        # Get yesterday's total
        total = await cache.hget(self.cost_key, yesterday_str)
        if total:
            # Could store in database for long-term history
            logger.info(f"Yesterday's AI cost: ${float(total):.4f}")
        
        # Clean up old entries (> 90 days)
        all_days = await cache.hkeys(self.cost_key)
        cutoff = date.today() - timedelta(days=90)
        
        for day_str in all_days:
            try:
                day_date = date.fromisoformat(day_str)
                if day_date < cutoff:
                    await cache.hdel(self.cost_key, day_str)
            except:
                pass
    
    async def save_to_database(self):
        """Persist cost data to PostgreSQL for long-term storage."""
        async with db_manager.session() as session:
            from ..models.ai_cost import AICost  # You'd need to create this model
            
            records = await self.get_recent_records(1)  # Last 24 hours
            
            for record in records:
                # Check if already saved
                # Insert if new
                pass


class CostOptimizationAdvisor:
    """Provides recommendations for cost optimization."""
    
    def __init__(self, tracker: AICostTracker):
        self.tracker = tracker
    
    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations."""
        summary = await self.tracker.get_summary()
        breakdown = summary["breakdown"]
        
        recommendations = []
        
        # Check if too many premium model calls
        # This would require tracking model per operation
        # For now, generic recommendations
        
        # Recommendation 1: Batch scoring
        if breakdown["scoring"]["count"] > 100:
            recommendations.append({
                "area": "scoring",
                "suggestion": "Consider batching scoring requests to reduce API overhead",
                "potential_savings": "~10-20%"
            })
        
        # Recommendation 2: Cache hit rate
        # Would need cache hit stats
        
        # Recommendation 3: Model downgrade for certain ops
        if breakdown["email_drafting"]["cost"] > 1.0:
            recommendations.append({
                "area": "email_drafting",
                "suggestion": "Consider using gpt-4o-mini for all email drafting (already using)",
                "potential_savings": "N/A"
            })
        
        # Recommendation 4: Review ambiguous cases
        if breakdown["scoring"]["count"] > 0:
            recommendations.append({
                "area": "scoring",
                "suggestion": "Review scoring threshold - ambiguous cases (40-70) use premium model",
                "potential_savings": "Adjust threshold to reduce premium calls"
            })
        
        return recommendations