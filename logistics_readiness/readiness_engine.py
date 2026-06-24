"""Readiness Engine - Module 8 for Sprint 13."""
from typing import Dict, Any, Optional


class ReadinessEngine:
    def __init__(self):
        self.reports: Dict[str, Any] = {}

    def assess_readiness(self, asset_id: str, metrics: Dict[str, float]) -> float:
        weights = {
            "health": 0.4,
            "fuel": 0.2,
            "maintenance_due": 0.2,
            "communications": 0.2,
        }
        
        score = 0.0
        for key, weight in weights.items():
            score += metrics.get(key, 1.0) * weight
        
        self.reports[asset_id] = {
            "asset_id": asset_id,
            "readiness_score": score,
            "metrics": metrics,
        }
        return score

    def get_readiness_report(self, asset_id: str) -> Optional[Any]:
        return self.reports.get(asset_id)
