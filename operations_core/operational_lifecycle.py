"""Operational Lifecycle - Module 10 for Sprint 13."""
from typing import Dict, Any, List
from datetime import datetime


class OperationalLifecycle:
    def __init__(self):
        self.lifecycles: Dict[str, List[Dict[str, Any]]] = {}

    def record_event(
        self,
        operation_id: str,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        if operation_id not in self.lifecycles:
            self.lifecycles[operation_id] = []
        self.lifecycles[operation_id].append({
            "type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_lifecycle(self, operation_id: str) -> List[Dict[str, Any]]:
        return self.lifecycles.get(operation_id, [])

    def get_latest_event(self, operation_id: str) -> Dict[str, Any]:
        lifecycle = self.get_lifecycle(operation_id)
        return lifecycle[-1] if lifecycle else {}
