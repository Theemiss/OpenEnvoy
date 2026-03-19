"""Analytics and insights from feedback data."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict

from .collector import FeedbackCollector

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Generate insights from feedback data."""
    
    def __init__(self):
        self.collector = FeedbackCollector()
    
    async def generate_insights(self) -> List[Dict[str, Any]]:
        """Generate actionable insights."""
        
        insights = []
        
        # Get data
        summary = await self.collector.get_feedback_summary()
        month_data = summary.get("last_30_days", {})
        
        if not month_data:
            return insights
        
        # Insight 1: Score threshold optimization
        score_performance = month_data.get("by_score", {})
        if score_performance:
            # Find optimal threshold
            thresholds = []
            for range_name, stats in score_performance.items():
                if stats["count"] >= 5:
                    thresholds.append({
                        "range": range_name,
                        "interview_rate": stats["interview_rate"],
                        "count": stats["count"]
                    })
            
            if thresholds:
                best = max(thresholds, key=lambda x: x["interview_rate"])
                current_threshold = 70  # Current system threshold
                
                # Extract min score from range name
                try:
                    min_score = int(best["range"].split("-")[0])
                    if min_score != current_threshold and best["count"] >= 10:
                        insights.append({
                            "type": "threshold_optimization",
                            "title": "Score Threshold Optimization",
                            "description": f"Jobs scored {best['range']} have {best['interview_rate']}% interview rate. Consider adjusting threshold.",
                            "current": current_threshold,
                            "suggested": min_score,
                            "confidence": "medium" if best["count"] < 20 else "high",
                            "data": best
                        })
                except:
                    pass
        
        # Insight 2: Company response patterns
        companies = month_data.get("top_companies", [])
        good_companies = [c for c in companies if c["response_rate"] > 50 and c["count"] >= 3]
        
        if good_companies:
            insights.append({
                "type": "company_insight",
                "title": "High-Response Companies",
                "description": f"Found {len(good_companies)} companies with >50% response rate",
                "companies": good_companies[:5],
                "recommendation": "Prioritize these companies in future applications"
            })
        
        # Insight 3: Email pattern effectiveness
        email_patterns = summary.get("email_performance", {}).get("email_patterns", [])
        if email_patterns and len(email_patterns) >= 2:
            best_pattern = email_patterns[0]
            worst_pattern = email_patterns[-1]
            
            if best_pattern["response_rate"] - worst_pattern["response_rate"] > 20:
                insights.append({
                    "type": "email_optimization",
                    "title": "Email Style Impact",
                    "description": f"'{best_pattern['pattern']}' style emails perform {best_pattern['response_rate']}% vs '{worst_pattern['pattern']}' at {worst_pattern['response_rate']}%",
                    "best_pattern": best_pattern,
                    "worst_pattern": worst_pattern,
                    "recommendation": f"Use more {best_pattern['pattern']} style emails"
                })
        
        # Insight 4: Response time analysis
        outcomes = await self.collector.collect_application_outcomes(30)
        response_times = [o["response_time"] for o in outcomes if o["response_time"]]
        
        if response_times:
            avg_response = np.mean(response_times)
            median_response = np.median(response_times)
            
            insights.append({
                "type": "response_time",
                "title": "Response Time Analysis",
                "description": f"Average response time: {avg_response:.1f} hours, Median: {median_response:.1f} hours",
                "avg_hours": round(avg_response, 1),
                "median_hours": round(median_response, 1),
                "recommendation": f"Follow up after {int(median_response * 1.5)} hours if no response"
            })
        
        # Insight 5: Skills that correlate with interviews
        if outcomes:
            # Collect skills from jobs that led to interviews
            interviewed_skills = []
            all_skills = []
            
            for o in outcomes:
                if o["job"] and o["job"].skills:
                    if o["status"] == "interviewing":
                        interviewed_skills.extend(o["job"].skills)
                    all_skills.extend(o["job"].skills)
            
            if interviewed_skills and all_skills:
                # Find overrepresented skills
                from collections import Counter
                interviewed_counter = Counter(interviewed_skills)
                all_counter = Counter(all_skills)
                
                skill_ratios = []
                for skill, count in interviewed_counter.items():
                    if all_counter[skill] > 0:
                        ratio = count / all_counter[skill]
                        if ratio > 1.5 and count >= 3:
                            skill_ratios.append({
                                "skill": skill,
                                "ratio": round(ratio, 2),
                                "interview_count": count,
                                "total_count": all_counter[skill]
                            })
                
                if skill_ratios:
                    insights.append({
                        "type": "skill_correlation",
                        "title": "High-Impact Skills",
                        "description": f"Skills that correlate with interview success",
                        "skills": sorted(skill_ratios, key=lambda x: x["ratio"], reverse=True)[:5]
                    })
        
        return insights
    
    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report."""
        
        summary = await self.collector.get_feedback_summary()
        insights = await self.generate_insights()
        
        # Add recommendations
        recommendations = []
        
        for insight in insights:
            if insight["type"] == "threshold_optimization":
                recommendations.append({
                    "area": "scoring",
                    "action": f"Consider changing score threshold from {insight['current']} to {insight['suggested']}",
                    "expected_impact": "Better focus on high-potential jobs",
                    "confidence": insight["confidence"]
                })
            
            elif insight["type"] == "email_optimization":
                recommendations.append({
                    "area": "email",
                    "action": f"Use '{insight['best_pattern']['pattern']}' email style more frequently",
                    "expected_impact": f"Potential {insight['best_pattern']['response_rate'] - insight['worst_pattern']['response_rate']}% increase in response rate",
                    "confidence": "high"
                })
        
        return {
            "generated_at": datetime.now().isoformat(),
            "period": "last_30_days",
            "summary": summary,
            "insights": insights,
            "recommendations": recommendations,
            "data_quality": {
                "total_applications": summary.get("last_30_days", {}).get("total_applications", 0),
                "has_enough_data": summary.get("last_30_days", {}).get("total_applications", 0) > 20
            }
        }