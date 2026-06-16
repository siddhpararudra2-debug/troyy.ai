import time
import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from validation.schemas.validation import (
    ValidationRequest, ValidationResponse, RiskAssessmentResponse, 
    ApprovalResponse, AuditReportResponse, ValidationIssueSchema
)
from validation.services.unit_validator import UnitValidator
from validation.services.assumptions_validator import AssumptionsValidator
from validation.services.safety_factor_validator import SafetyFactorValidator
from validation.services.risk_assessment_service import RiskAssessmentService
from validation.services.approval_service import ApprovalEngine
from validation.models.database import ValidationRun, ValidationIssue, RiskAssessment, ApprovalDecision, AuditLog

# Mock DB dependency for easy IDE testing (replace with actual get_db in production)
def get_db():
    class MockSession:
        def add(self, obj): obj.id = 1
        def commit(self): pass
        def flush(self): pass
        def query(self, model): 
            class MockQuery:
                def filter(self, *args): return self
                def all(self): return []
                def first(self): return None
            return MockQuery()
    return MockSession()

router = APIRouter(prefix="/validation", tags=["Validation Engine"])

@router.post("/validate", response_model=ValidationResponse)
async def run_validation_pipeline(request: ValidationRequest, db: Session = Depends(get_db)):
    start_time = time.perf_counter()
    
    run = ValidationRun(project_id=request.project_id, solver_run_id=request.solver_run_id, status="RUNNING")
    db.add(run)
    db.flush()
    
    unit_val = UnitValidator()
    assumption_val = AssumptionsValidator()
    safety_val = SafetyFactorValidator()
    
    # Parallel execution ensures we hit the <500ms target for independent checks
    results = await asyncio.gather(
        unit_val.validate(request.model_dump()),
        assumption_val.validate(request.model_dump()),
        safety_val.validate(request.model_dump())
    )
    
    all_issues = []
    for issue_list in results:
        all_issues.extend(issue_list)
        for issue in issue_list:
            db_issue = ValidationIssue(
                run_id=run.id,
                module=issue.module,
                severity=issue.severity,
                description=issue.description,
                engineering_reasoning=issue.engineering_reasoning,
                recommendation=issue.recommendation
            )
            db.add(db_issue)
    
    # Early exit for Critical failures to save compute
    if any(i.severity.value == "CRITICAL" for i in all_issues):
        run.status = "FAILED_CRITICAL"
        db.commit()
        execution_time = (time.perf_counter() - start_time) * 1000
        return ValidationResponse(run_id=run.id, status="REJECTED", issues=all_issues, execution_time_ms=execution_time)

    run.status = "COMPLETED"
    db.commit()
    
    execution_time = (time.perf_counter() - start_time) * 1000
    return ValidationResponse(run_id=run.id, status="PASSED", issues=all_issues, execution_time_ms=execution_time)

@router.post("/risk-analysis", response_model=RiskAssessmentResponse)
async def analyze_risk(run_id: int, db: Session = Depends(get_db)):
    issues = db.query(ValidationIssue).filter(ValidationIssue.run_id == run_id).all()
    
    issue_schemas = [
        ValidationIssueSchema(
            module=i.module, severity=i.severity, description=i.description,
            engineering_reasoning=i.engineering_reasoning, recommendation=i.recommendation
        ) for i in issues
    ]
    
    risk_service = RiskAssessmentService()
    risk_report = await risk_service.assess(issue_schemas)
    
    db_risk = RiskAssessment(
        run_id=run_id,
        overall_risk_level=risk_report.overall_risk_level,
        risk_matrix=risk_report.risk_matrix
    )
    db.add(db_risk)
    db.commit()
    
    return risk_report

@router.post("/approval", response_model=ApprovalResponse)
async def make_approval_decision(run_id: int, db: Session = Depends(get_db)):
    issues = db.query(ValidationIssue).filter(ValidationIssue.run_id == run_id).all()
    risk = db.query(RiskAssessment).filter(RiskAssessment.run_id == run_id).first()
    
    if not risk:
        raise HTTPException(status_code=400, detail="Risk assessment must be completed before approval.")
        
    issue_schemas = [
        ValidationIssueSchema(
            module=i.module, severity=i.severity, description=i.description,
            engineering_reasoning=i.engineering_reasoning, recommendation=i.recommendation
        ) for i in issues
    ]
    
    risk_response = RiskAssessmentResponse(overall_risk_level=risk.overall_risk_level, risk_matrix=risk.risk_matrix)
    
    approval_engine = ApprovalEngine()
    decision = await approval_engine.decide(issue_schemas, risk_response)
    
    db_decision = ApprovalDecision(
        run_id=run_id,
        status=decision.status,
        engineering_reasoning=decision.engineering_reasoning,
        risk_summary=decision.risk_summary,
        validation_summary=decision.validation_summary
    )
    db.add(db_decision)
    
    if decision.status.value == "REJECTED":
        log = AuditLog(
            action="REJECTION",
            details={"run_id": run_id},
            lessons_learned=decision.engineering_reasoning
        )
        db.add(log)
        
    db.commit()
    return decision
