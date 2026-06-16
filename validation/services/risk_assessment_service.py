from typing import List, Dict, Any
from validation.schemas.validation import ValidationIssueSchema, Severity, RiskAssessmentResponse

class RiskAssessmentService:
    PROBABILITY_MAP = {
        Severity.LOW: "Rare",
        Severity.MEDIUM: "Unlikely",
        Severity.HIGH: "Likely",
        Severity.CRITICAL: "Almost Certain"
    }
    
    IMPACT_MAP = {
        Severity.LOW: "Minor performance degradation",
        Severity.MEDIUM: "Mission delay or component replacement",
        Severity.HIGH: "Mission failure or significant damage",
        Severity.CRITICAL: "Catastrophic failure, loss of life or asset"
    }

    async def assess(self, issues: List[ValidationIssueSchema]) -> RiskAssessmentResponse:
        if not issues:
            return RiskAssessmentResponse(overall_risk_level=Severity.LOW, risk_matrix=[])
        
        risk_matrix = []
        max_severity = Severity.LOW
        
        for issue in issues:
            if self._severity_rank(issue.severity) > self._severity_rank(max_severity):
                max_severity = issue.severity
                
            risk_matrix.append({
                "description": issue.description,
                "cause": issue.module,
                "severity": issue.severity.value,
                "probability": self.PROBABILITY_MAP[issue.severity],
                "impact": self.IMPACT_MAP[issue.severity],
                "recommended_fix": issue.recommendation
            })
            
        return RiskAssessmentResponse(overall_risk_level=max_severity, risk_matrix=risk_matrix)

    def _severity_rank(self, severity: Severity) -> int:
        return {Severity.LOW: 1, Severity.MEDIUM: 2, Severity.HIGH: 3, Severity.CRITICAL: 4}[severity]
