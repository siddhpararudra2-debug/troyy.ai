from review_council.services.design_review_service import DesignReviewService
from review_council.services.chief_engineer_agent import ChiefEngineerAgent
from review_council.schemas.review_models import ReviewCategory, ApprovalDecision, ReviewReport

def test_structural_review_pass():
    svc = DesignReviewService("Structural Reviewer", ReviewCategory.STRUCTURAL)
    report = svc.review_design("P1", {"factor_of_safety": 2.5})
    assert report.final_results['decision'] == ApprovalDecision.APPROVED.value

def test_structural_review_fail():
    svc = DesignReviewService("Structural Reviewer", ReviewCategory.STRUCTURAL)
    report = svc.review_design("P1", {"factor_of_safety": 1.2})
    assert report.final_results['decision'] == ApprovalDecision.REJECTED.value

def test_safety_review_showstopper():
    svc = DesignReviewService("Safety Reviewer", ReviewCategory.SAFETY)
    report = svc.review_design("P1", {"emergency_stop": False})
    assert report.final_results['decision'] == ApprovalDecision.REJECTED.value
    assert any(f['severity'] == 'SHOWSTOPPER' for f in report.final_results['review_report']['findings'])

def test_chief_arbitrate():
    chief = ChiefEngineerAgent()
    reports = [
        ReviewReport(project_id="P1", design_ref="D1", reviewer_role="R1", 
                     category=ReviewCategory.STRUCTURAL, findings=[], 
                     decision=ApprovalDecision.APPROVED, justification="OK"),
        ReviewReport(project_id="P1", design_ref="D1", reviewer_role="R2",
                     category=ReviewCategory.SAFETY, findings=[],
                     decision=ApprovalDecision.APPROVED, justification="OK")
    ]
    decision = chief.arbitrate("P1", reports)
    assert decision.decision == ApprovalDecision.APPROVED
