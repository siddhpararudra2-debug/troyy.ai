"""
Compliance Checker - Checks designs against requirements and standards.

Capabilities:
- Standards Compliance
- Requirements Compliance
- Best Practices Checking
"""

from typing import Optional, List, Dict, Any
from datetime import datetime


class ComplianceChecker:
    """Checks engineering designs for compliance with requirements and standards."""

    def __init__(self):
        self._standards: Dict[str, List[str]] = {
            "ISO-9001": ["quality_management", "documentation", "audit_trail"],
            "ISO-26262": ["functional_safety", "hazard_analysis", "safety_goals"],
            "DO-178C": ["software_development", "verification", "configuration_management"],
            "MIL-STD-882": ["system_safety", "hazard_tracking", "risk_assessment"],
        }

    def check_standards_compliance(self, design_data: Dict[str, Any],
                                    standards: List[str]) -> Dict[str, Any]:
        results = []
        compliant = True
        for std in standards:
            requirements = self._standards.get(std, [])
            met = sum(1 for r in requirements if any(r in str(v).lower() for v in design_data.values()))
            total = len(requirements)
            compliance_pct = (met / total * 100) if total > 0 else 0
            compliant = compliant and compliance_pct >= 80
            results.append({"standard": std, "requirements_met": met,
                           "total_requirements": total, "compliance_pct": round(compliance_pct, 1)})
        return {"compliant": compliant, "results": results, "checked_at": datetime.utcnow().isoformat()}

    def check_requirements_traceability(self, requirements: List[str],
                                         design_elements: List[str]) -> Dict[str, Any]:
        traced = [r for r in requirements if any(r in str(d) for d in design_elements)]
        return {
            "total_requirements": len(requirements),
            "traced_requirements": len(traced),
            "traceability_pct": round(len(traced) / len(requirements) * 100, 1) if requirements else 0,
            "untraced": [r for r in requirements if r not in traced],
        }