"""Approval Manager - Review & Approval for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class ApprovalManager:
    """Manage approvals."""

    def __init__(self):
        self.approvals: Dict[str, Dict[str, Any]] = {}

    def request_approval(
        self,
        review_id: str,
        approval_type: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Request an approval."""
        approval_id = str(uuid.uuid4())
        approval = {
            "id": approval_id,
            "review_id": review_id,
            "approval_type": approval_type,
            "description": description,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        self.approvals[approval_id] = approval
        return approval

    def grant_approval(
        self,
        approval_id: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Grant an approval."""
        if approval_id in self.approvals:
            self.approvals[approval_id]["status"] = "approved"
            self.approvals[approval_id]["notes"] = notes
            self.approvals[approval_id]["signed_at"] = datetime.utcnow().isoformat()
            return self.approvals[approval_id]
        return None

    def deny_approval(
        self,
        approval_id: str,
        reason: str
    ) -> Optional[Dict[str, Any]]:
        """Deny an approval."""
        if approval_id in self.approvals:
            self.approvals[approval_id]["status"] = "denied"
            self.approvals[approval_id]["reason"] = reason
            return self.approvals[approval_id]
        return None
