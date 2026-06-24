"""Engineering Journal - Knowledge Base for Sprint 17."""
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any


class EngineeringJournal:
    """Personal engineering journal and logbook."""

    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}

    def add_entry(
        self,
        project_id: str,
        content: str,
        entry_type: str = "note",
        entry_date: Optional[date] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a journal entry."""
        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "project_id": project_id,
            "content": content,
            "entry_type": entry_type,
            "entry_date": (entry_date or date.today()).isoformat(),
            "tags": tags or [],
            "created_at": datetime.utcnow().isoformat()
        }
        self.entries[entry_id] = entry
        return entry

    def get_entries(
        self,
        project_id: Optional[str] = None,
        entry_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get journal entries, optionally filtered."""
        entries = list(self.entries.values())
        if project_id:
            entries = [e for e in entries if e["project_id"] == project_id]
        if entry_type:
            entries = [e for e in entries if e["entry_type"] == entry_type]
        return sorted(entries, key=lambda x: x["entry_date"], reverse=True)
