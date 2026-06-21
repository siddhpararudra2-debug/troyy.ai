from typing import Dict
from verification.schemas.engineering_report import ReportContext, EngineeringReport
from review_council.schemas.review_models import ReviewCategory, ReviewFinding, ReviewReport, FindingSeverity, ApprovalDecision

class DesignReviewService:
    def __init__(self, reviewer_role: str, category: ReviewCategory):
        self.reviewer_role = reviewer_role
        self.category = category
        
    def review_design(self, project_id: str, design_data: Dict) -> EngineeringReport:
        with ReportContext(
            requirements=[f"Perform {self.category.value} design review as {self.reviewer_role}"],
            assumptions=["Design data is complete and accurate", "Review criteria are well-defined"],
            constraints=["Every finding must cite evidence", "Decision must be justified"],
            formula_selection="Criteria-Based Evaluation",
            formula_explanation="Evaluates design against category-specific engineering criteria.",
            unit_analysis="Findings are categorical, severity is ordinal."
        ) as ctx:
            findings = []
            
            if self.category == ReviewCategory.STRUCTURAL:
                fos = design_data.get('factor_of_safety', 1.0)
                if fos < 1.5:
                    findings.append(ReviewFinding(
                        category=self.category,
                        severity=FindingSeverity.CRITICAL,
                        title="Insufficient Factor of Safety",
                        description=f"FoS = {fos}, minimum required = 1.5",
                        evidence=[f"Calculated FoS: {fos}", "Industry standard: ≥1.5"],
                        recommendation="Increase cross-section or select higher-strength material",
                        raised_by=self.reviewer_role
                    ))
                if fos < 2.0:
                    findings.append(ReviewFinding(
                        category=self.category,
                        severity=FindingSeverity.MAJOR,
                        title="Marginal Factor of Safety",
                        description=f"FoS = {fos}, recommended = 2.0+",
                        evidence=["Best practice: FoS ≥ 2.0 for dynamic loads"],
                        recommendation="Consider design margin increase",
                        raised_by=self.reviewer_role
                    ))
                    
            elif self.category == ReviewCategory.THERMAL:
                max_temp = design_data.get('max_temperature_c', 25)
                limit = design_data.get('max_allowed_temp_c', 85)
                margin = (limit - max_temp) / limit
                if margin < 0.1:
                    findings.append(ReviewFinding(
                        category=self.category,
                        severity=FindingSeverity.MAJOR,
                        title="Insufficient Thermal Margin",
                        description=f"Thermal margin = {margin*100:.1f}%, minimum = 10%",
                        evidence=[f"Max temp: {max_temp}°C", f"Limit: {limit}°C"],
                        recommendation="Add heat sinking or reduce power dissipation",
                        raised_by=self.reviewer_role
                    ))
                    
            elif self.category == ReviewCategory.SAFETY:
                if not design_data.get('emergency_stop', False):
                    findings.append(ReviewFinding(
                        category=self.category,
                        severity=FindingSeverity.SHOWSTOPPER,
                        title="Missing Emergency Stop",
                        description="System lacks emergency stop function",
                        evidence=["ISO 10218-1 clause 5.3 requires E-stop"],
                        recommendation="Implement hardware E-stop with category 0 or 1 stop",
                        raised_by=self.reviewer_role
                    ))
                    
            severities = [f.severity for f in findings]
            if FindingSeverity.SHOWSTOPPER in severities or FindingSeverity.CRITICAL in severities:
                decision = ApprovalDecision.REJECTED
                justification = "Critical or showstopper findings require redesign."
            elif FindingSeverity.MAJOR in severities:
                decision = ApprovalDecision.REQUIRES_REVISION
                justification = "Major findings require resolution before approval."
            elif findings:
                decision = ApprovalDecision.APPROVED_WITH_CONCERNS
                justification = "Minor findings noted but design acceptable."
            else:
                decision = ApprovalDecision.APPROVED
                justification = "Design meets all review criteria."
                
            report = ReviewReport(
                project_id=project_id,
                design_ref=design_data.get('ref', 'unknown'),
                reviewer_role=self.reviewer_role,
                category=self.category,
                findings=findings,
                decision=decision,
                justification=justification
            )
            
            ctx.add_matrix_op("Review Evaluation", "D = f(severities)", {"findings": len(findings)})
            
            ctx.finalize(
                final_results={
                    "review_report": report.dict(),
                    "findings_count": len(findings),
                    "decision": decision.value,
                    "severity_breakdown": {s.value: severities.count(s) for s in set(severities)}
                },
                interpretation=f"{self.reviewer_role} review: {decision.value}. {len(findings)} findings."
            )
        return ctx.report
