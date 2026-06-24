"""
Document Management System Module
Provides document management, versioning, and approvals.
"""
from app.documents.document_manager import DocumentManager
from app.documents.version_manager import VersionManager
from app.documents.approval_manager import ApprovalManager

__all__ = [
    "DocumentManager",
    "VersionManager",
    "ApprovalManager",
]
