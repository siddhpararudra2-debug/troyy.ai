"""
Risk Engine - Risk identification, assessment, and management platform.

Capabilities:
- Risk Identification
- Risk Assessment
- Risk Register Management
- Probability/Impact Analysis
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class RiskCategory(str, Enum):
    """Categories of engineering risks."""
    TECHNICAL = "technical"
    SCHEDULE = "schedule"
    COST = "cost"
    SAFETY = "safety"
    PERFORMANCE = "performance"
    MANUFACTURING = "manufacturing"
    SUPPLIER = "supplier"
    REGULATORY = "regulatory"
    ENVIRONMENTAL = "environmental"
    OPERATIONAL = "operational"


class RiskLevel(str, Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


class RiskStatus(str, Enum):
    """Status of risk mitigation."""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class Risk:
    """An engineering risk item."""

    def __init__(
        self,
        risk_id: str,
        title: str,
        description: str,
        category: RiskCategory = RiskCategory.TECHNICAL,
        probability: float = 0.5,
        impact: float = 0.5,
        status: RiskStatus = RiskStatus.IDENTIFIED,
        owner: Optional[str] = None,
    ):
        self.id = risk_id
        self.title = title
        self.description = description
        self.category = category
        self.probability = max(0.0, min(1.0, probability))
        self.impact = max(0.0, min(1.0, impact))
        self.status = status
        self.owner = owner
        self.mitigations: List[str] = []
        self.triggers: List[str] = []
        self.related_requirements: List[str] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    @property
    def risk_score(self) -> float:
        return round(self.probability * self.impact, 2)

    @property
    def risk_level(self) -> RiskLevel:
        score = self.risk_score
        if score >= 0.7:
            return RiskLevel.CRITICAL
        elif score >= 0.5:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        elif score >= 0.1:
            return RiskLevel.LOW
        return RiskLevel.NEGLIGIBLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "probability": self.probability,
            "impact": self.impact,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "owner": self.owner,
            "mitigations": self.mitigations,
            "triggers": self.triggers,
            "related_requirements": self.related_requirements,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class RiskEngine:
    """Manages risk identification, assessment, and mitigation."""

    def __init__(self):
        self._risks: Dict[str, Risk] = {}

    def create_risk(
        self,
        title: str,
        description: str,
        category: RiskCategory = RiskCategory.TECHNICAL,
        probability: float = 0.5,
        impact: float = 0.5,
        owner: Optional[str] = None,
    ) -> Risk:
        risk_id = str(uuid.uuid4())
        risk = Risk(risk_id, title, description, category, probability, impact, owner=owner)
        self._risks[risk_id] = risk
        return risk

    def get_risk(self, risk_id: str) -> Optional[Risk]:
        return self._risks.get(risk_id)

    def update_risk(self, risk_id: str, **kwargs) -> Optional[Risk]:
        risk = self._risks.get(risk_id)
        if risk:
            for key, value in kwargs.items():
                if hasattr(risk, key):
                    setattr(risk, key, value)
            risk.updated_at = datetime.utcnow()
        return risk

    def get_all_risks(self) -> List[Risk]:
        return list(self._risks.values())

    def get_risks_by_level(self, level: RiskLevel) -> List[Risk]:
        return [r for r in self._risks.values() if r.risk_level == level]

    def get_risks_by_category(self, category: RiskCategory) -> List[Risk]:
        return [r for r in self._risks.values() if r.category == category]

    def generate_risk_register(self) -> Dict[str, Any]:
        risks = self.get_all_risks()
        by_level: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        for r in risks:
            by_level[r.risk_level.value] = by_level.get(r.risk_level.value, 0) + 1
            by_category[r.category.value] = by_category.get(r.category.value, 0) + 1

        return {
            "total_risks": len(risks),
            "by_level": by_level,
            "by_category": by_category,
            "critical_risks": [r.to_dict() for r in self.get_risks_by_level(RiskLevel.CRITICAL)],
            "high_risks": [r.to_dict() for r in self.get_risks_by_level(RiskLevel.HIGH)],
            "all_risks": [r.to_dict() for r in risks],
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_top_risks(self, n: int = 10) -> List[Risk]:
        return sorted(self._risks.values(), key=lambda r: r.risk_score, reverse=True)[:n]