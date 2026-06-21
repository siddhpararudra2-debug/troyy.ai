from typing import List
from review_council.schemas.review_models import ReviewReport, CouncilDecision, ApprovalDecision

class ChiefEngineerAgent:
    def arbitrate(self, project_id: str, review_reports: List[ReviewReport]) -> CouncilDecision:
        all_findings = []
        decisions = []
        
        for report in review_reports:
            all_findings.extend(report.findings)
            decisions.append(report.decision)
            
        severity_counts = {}
        for f in all_findings:
            severity_counts[f.severity.value] = severity_counts.get(f.severity.value, 0) + 1
            
        if severity_counts.get('SHOWSTOPPER', 0) > 0 or severity_counts.get('CRITICAL', 0) > 2:
            final_decision = ApprovalDecision.REJECTED
            summary = "Project rejected due to critical safety or design flaws."
            actions = [f"Resolve: {f.title}" for f in all_findings if f.severity.value in ['SHOWSTOPPER', 'CRITICAL']]
        elif ApprovalDecision.REJECTED in decisions:
            final_decision = ApprovalDecision.REQUIRES_REVISION
            summary = "One or more reviews rejected. Revision required."
            actions = [f"Address {r.reviewer_role} concerns: {r.justification}" for r in review_reports if r.decision == ApprovalDecision.REJECTED]
        elif ApprovalDecision.REQUIRES_REVISION in decisions:
            final_decision = ApprovalDecision.REQUIRES_REVISION
            summary = "Reviews require revision before approval."
            actions = [f"Resolve: {f.title}" for f in all_findings if f.severity.value in ['MAJOR', 'CRITICAL']]
        elif ApprovalDecision.APPROVED_WITH_CONCERNS in decisions:
            final_decision = ApprovalDecision.APPROVED_WITH_CONCERNS
            summary = "Approved with noted concerns."
            actions = [f"Monitor: {f.title}" for f in all_findings if f.severity.value == 'MINOR']
        else:
            final_decision = ApprovalDecision.APPROVED
            summary = "All reviews passed. Design approved for release."
            actions = []
            
        return CouncilDecision(
            project_id=project_id,
            decision=final_decision,
            summary=summary,
            findings_summary=severity_counts,
            required_actions=actions
        )
