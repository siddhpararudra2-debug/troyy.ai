from documentation.models.database import DecisionLog, ProjectHistory
from documentation.schemas.documentation import DecisionLogCreate
from sqlalchemy.orm import Session

class DecisionLogService:
    def __init__(self, db: Session):
        self.db = db

    def log_decision(self, data: DecisionLogCreate) -> int:
        decision = DecisionLog(
            project_id=data.project_id,
            project_report_id=1, # Mock linkage for simplicity
            decision_title=data.decision_title,
            decision_description=data.decision_description,
            reasoning=data.reasoning,
            benefits=data.benefits,
            risks=data.risks
        )
        self.db.add(decision)
        
        # Append to Project History (Append-only for audit)
        history = ProjectHistory(
            project_id=data.project_id,
            event_type="DECISION_LOGGED",
            details={
                "decision": data.decision_title,
                "reasoning": data.reasoning
            },
            actor="ENGINEER"
        )
        self.db.add(history)
        self.db.commit()
        return decision.id
