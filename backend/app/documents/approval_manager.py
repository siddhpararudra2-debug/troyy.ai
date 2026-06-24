"""
Approval Manager for Documents Module
Manages document approvals.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ApprovalManager:
    """
    Manages document approval workflows.
    """

    def __init__(self):
        self._approvals: Dict[str, List[Dict[str, Any]]] = {}

    async def request_approval(
        self,
        doc_id: str,
        user_id: str,
        approver_ids: List[str],
    ) -> Dict[str, Any]:
        """
        Request document approval.
        """
        approval_id = str(uuid.uuid4())
        approval = {
            "id": approval_id,
            "doc_id": doc_id,
            "requested_by": user_id,
            "approvers": approver_ids,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        if doc_id not in self._approvals:
            self._approvals[doc_id] = []
        self._approvals[doc_id].append(approval)
        return approval
