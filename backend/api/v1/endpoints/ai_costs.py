"""AI costs and monitoring endpoints."""

from fastapi import APIRouter

from ....ai.cost_tracker import AICostTracker, CostOptimizationAdvisor

router = APIRouter(prefix="/ai/costs", tags=["ai", "costs"])


@router.get("/summary")
async def get_cost_summary():
    """Get AI cost summary."""
    tracker = AICostTracker()
    summary = await tracker.get_summary()
    return summary


@router.get("/breakdown")
async def get_cost_breakdown(days: int = 7):
    """Get cost breakdown by operation."""
    tracker = AICostTracker()
    breakdown = await tracker.get_operation_breakdown(days)
    return breakdown


@router.get("/daily")
async def get_daily_costs(days: int = 30):
    """Get daily costs for last N days."""
    tracker = AICostTracker()
    costs = await tracker.get_daily_costs(days)
    return {"daily_costs": costs}


@router.get("/recommendations")
async def get_recommendations():
    """Get cost optimization recommendations."""
    tracker = AICostTracker()
    advisor = CostOptimizationAdvisor(tracker)
    recommendations = await advisor.get_recommendations()
    return {"recommendations": recommendations}
