from sqlalchemy.orm import Session
from documentation.models.database import KnowledgeEntry, KnowledgeCategory
from documentation.schemas.documentation import KnowledgeEntryResponse

class KnowledgeCaptureService:
    def __init__(self, db: Session):
        self.db = db

    def extract_lessons_from_rejection(self, project_id: str, rejection_reason: str):
        """Automatically capture knowledge when a design is rejected by Day 7 Engine"""
        entry = KnowledgeEntry(
            category=KnowledgeCategory.COMMON_FAILURE,
            title=f"Failure Mode: {project_id}",
            content=rejection_reason,
            tags=["rejection", "safety", "validation"],
            source_project_id=project_id
        )
        self.db.add(entry)
        self.db.commit()

    def search_knowledge(self, query: str, category: str = None) -> list:
        # Performance: Simple ILIKE for demo. Production should use pg_trgm or Elasticsearch.
        q = self.db.query(KnowledgeEntry)
        if category:
            q = q.filter(KnowledgeEntry.category == category)
        q = q.filter(KnowledgeEntry.content.ilike(f"%{query}%")).limit(20)
        
        results = q.all()
        return [
            KnowledgeEntryResponse(
                id=k.id, category=k.category, title=k.title,
                content=k.content, tags=k.tags, source_project_id=k.source_project_id
            ) for k in results
        ]
