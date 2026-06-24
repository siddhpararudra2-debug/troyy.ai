"""Rehearsal Engine - Module 5 for Sprint 13."""
import uuid
from typing import List, Dict, Any, Optional


class RehearsalEngine:
    def __init__(self):
        self.rehearsals: Dict[str, Any] = {}

    def run_rehearsal(
        self,
        mission_id: str,
        scenario_id: str,
        participants: Optional[List[str]] = None
    ) -> str:
        rehearsal_id = str(uuid.uuid4())
        rehearsal = {
            "id": rehearsal_id,
            "mission_id": mission_id,
            "scenario_id": scenario_id,
            "participants": participants or [],
            "status": "running",
            "events": [],
            "progress": 0.0,
            "metrics": {
                "success_rate": 0.0,
                "timing_score": 0.0,
                "coordination_score": 0.0,
            },
        }
        self.rehearsals[rehearsal_id] = rehearsal
        return rehearsal_id

    def get_rehearsal(self, rehearsal_id: str) -> Any:
        return self.rehearsals.get(rehearsal_id)

    def list_rehearsals(self, mission_id: Optional[str] = None) -> List[Any]:
        rehearsals = list(self.rehearsals.values())
        if mission_id:
            rehearsals = [r for r in rehearsals if r["mission_id"] == mission_id]
        return rehearsals
