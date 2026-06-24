"""
Collaboration Platform Module
Provides comments, reviews, approvals, and discussions.
"""
from app.collaboration.comments_engine import CommentsEngine
from app.collaboration.review_engine import ReviewEngine
from app.collaboration.approval_workflow import ApprovalWorkflow
from app.collaboration.discussion_manager import DiscussionManager

__all__ = [
    "CommentsEngine",
    "ReviewEngine",
    "ApprovalWorkflow",
    "DiscussionManager",
]
