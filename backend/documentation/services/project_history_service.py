from sqlalchemy.orm import Session
from sqlalchemy import desc
from documentation.models.database import ProjectHistory
from documentation.schemas.documentation import ProjectHistoryResponse

class ProjectHistoryService:
    def __init__(self, db: Session):
        self.db = db

    def get_timeline(self, project_id: str, limit: int = 50) -> list:
        # Performance: Indexed query with limit ensures <100ms retrieval
        history = self.db.query(ProjectHistory).filter(
            ProjectHistory.project_id == project_id
        ).order_by(desc(ProjectHistory.timestamp)).limit(limit).all()
        
        return [
            ProjectHistoryResponse(
                id=h.id, project_id=h.project_id, timestamp=h.timestamp,
                event_type=h.event_type, details=h.details, actor=h.actor
            ) for h in history
        ]

    def log_event(self, project_id: str, event_type: str, details: dict, actor: str = "SYSTEM"):
        event = ProjectHistory(
            project_id=project_id,
            event_type=event_type,
            details=details,
            actor=actor
        )
        self.db.add(event)
        self.db.commit()
