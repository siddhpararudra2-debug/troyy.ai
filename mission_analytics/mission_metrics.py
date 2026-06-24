"""Mission Metrics - Module 9 for Sprint 13."""
from typing import Dict, Any
from enum import Enum


class MetricType(Enum):
    DURATION = "duration"
    DISTANCE = "distance"
    SUCCESS_RATE = "success_rate"
    EFFICIENCY = "efficiency"


class MissionMetrics:
    def __init__(self):
        self.metrics: Dict[str, Dict[MetricType, Any]] = {}

    def record_metric(
        self,
        mission_id: str,
        metric_type: MetricType,
        value: Any
    ) -> None:
        if mission_id not in self.metrics:
            self.metrics[mission_id] = {}
        self.metrics[mission_id][metric_type] = value

    def get_metrics(self, mission_id: str) -> Dict[MetricType, Any]:
        return self.metrics.get(mission_id, {})
