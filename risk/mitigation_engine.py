"""
Mitigation Engine - Risk mitigation planning and tracking.

Capabilities:
- Mitigation Planning
- Action Tracking
- Mitigation Effectiveness
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from risk.risk_engine import Risk, RiskStatus


class MitigationPlan:
    """A risk mitigation plan."""

    def __init__(self, plan_id: str, risk_id: str, description: str,
                 owner: Optional[str] = None, due_date: Optional[str] = None):
        self.id = plan_id
        self.risk_id = risk_id
        self.description = description
        self.owner = owner
        self.due_date = due_date
        self.actions: List[Dict[str, Any]] = []
        self.status = "planned"
        self.effectiveness: float = 0.0

    def add_action(self, action: str, owner: Optional[str] = None):
        self.actions.append({
            "id": str(uuid.uuid4()),
            "action": action,
            "owner": owner,
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "risk_id": self.risk_id,
            "description": self.description,
            "owner": self.owner,
            "due_date": self.due_date,
            "actions": self.actions,
            "status": self.status,
            "effectiveness": self.effectiveness,
        }


class MitigationEngine:
    """Plans and tracks risk mitigation activities."""

    def __init__(self):
        self._plans: Dict[str, MitigationPlan] = {}

    def create_mitigation_plan(self, risk: Risk, description: str,
                                owner: Optional[str] = None) -> MitigationPlan:
        plan_id = str(uuid.uuid4())
        plan = MitigationPlan(plan_id, risk.id, description, owner)
        self._plans[plan_id] = plan
        risk.mitigations.append(plan_id)
        risk.status = RiskStatus.MITIGATING
        return plan

    def get_plan(self, plan_id: str) -> Optional[MitigationPlan]:
        return self._plans.get(plan_id)

    def get_plans_for_risk(self, risk_id: str) -> List[MitigationPlan]:
        return [p for p in self._plans.values() if p.risk_id == risk_id]

    def get_all_plans(self) -> List[MitigationPlan]:
        return list(self._plans.values())

    def generate_mitigation_report(self) -> Dict[str, Any]:
        plans = self.get_all_plans()
        return {
            "total_plans": len(plans),
            "active_plans": len([p for p in plans if p.status == "active"]),
            "completed_plans": len([p for p in plans if p.status == "completed"]),
            "plans": [p.to_dict() for p in plans],
            "generated_at": datetime.utcnow().isoformat(),
        }