from typing import List
from validation.schemas.validation import ValidationIssueSchema, RiskAssessmentResponse, ApprovalResponse, ApprovalStatus, Severity

class ApprovalEngine:
    async def decide(self, issues: List[ValidationIssueSchema], risk_assessment: RiskAssessmentResponse) -> ApprovalResponse:
        critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
        high_count = sum(1 for i in issues if i.severity == Severity.HIGH)
        
        if critical_count > 0:
            status = ApprovalStatus.REJECTED
            reasoning = "REJECTED: Critical engineering flaws detected. Design violates fundamental physical or safety constraints."
        elif high_count > 2:
            status = ApprovalStatus.REQUIRES_REVISION
            reasoning = "REQUIRES REVISION: Multiple high-severity issues indicate systemic design weaknesses."
        elif high_count > 0 or risk_assessment.overall_risk_level in [Severity.HIGH, Severity.CRITICAL]:
            status = ApprovalStatus.APPROVED_WITH_CONCERNS
            reasoning = "APPROVED WITH CONCERNS: Design is viable but requires mitigation of identified high-risk items before production."
        else:
            status = ApprovalStatus.APPROVED
            reasoning = "APPROVED: Design meets all engineering requirements, safety margins, and dimensional consistency checks."
            
        return ApprovalResponse(
            status=status,
            engineering_reasoning=reasoning,
            risk_summary=f"Overall Risk: {risk_assessment.overall_risk_level.value}. {len(issues)} issues logged.",
            validation_summary=f"Validated parameters. {critical_count} critical, {high_count} high severity."
        )
