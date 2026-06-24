"""Change Approver - Change Management for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class ChangeApprover:
    """Approve or reject change requests."""

    def __init__(self):
        self.approvals: Dict[str, Dict[str, Any]] = {}

    def approve_change(self, change_id: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Approve a change request."""
        approval_id = str(uuid.uuid4())
        approval = {
            "id": approval_id,
            "change_id": change_id,
            "status": "approved",
            "notes": notes,
            "approved_at": datetime.utcnow().isoformat()
        }
        self.approvals[approval_id] = approval
        return approval

    def reject_change(self, change_id: str, reason: str) -> Dict[str, Any]:
        """Reject a change request."""
        approval_id = str(uuid.uuid4())
        approval = {
            "id": approval_id,
            "change_id": change_id,
            "status": "rejected",
            "reason": reason,
            "rejected_at": datetime.utcnow().isoformat()
        }
        self.approvals[approval_id] = approval
        return approval
