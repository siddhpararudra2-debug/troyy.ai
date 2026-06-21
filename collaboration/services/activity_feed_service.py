from typing import List, Optional
from collaboration.schemas.collab_models import ActivityEvent

class ActivityFeedService:
    def __init__(self, workspace_service):
        self.workspace_service = workspace_service
        
    def get_feed(self, workspace_id: str, limit: int = 50,
                entity_type: Optional[str] = None) -> List[ActivityEvent]:
        events = [e for e in self.workspace_service.activity_log
                 if e.workspace_id == workspace_id]
        if entity_type:
            events = [e for e in events if e.entity_type == entity_type]
        # Sort by timestamp descending, return most recent
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[:limit]
