"""Review Manager - Review & Approval for Sprint 17."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any


class ReviewManager:
    """Manage engineering reviews."""

    def __init__(self):
        self.reviews: Dict[str, Dict[str, Any]] = {}

    def create_review(
        self,
        project_id: str,
        artifact_id: str,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new review."""
        review_id = str(uuid.uuid4())
        review = {
            "id": review_id,
            "project_id": project_id,
            "artifact_id": artifact_id,
            "title": title,
            "description": description,
            "status": "pending",
            "comments": [],
            "created_at": datetime.utcnow().isoformat()
        }
        self.reviews[review_id] = review
        return review

    def add_comment(
        self,
        review_id: str,
        comment: str,
        commenter: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Add a comment to a review."""
        if review_id not in self.reviews:
            return None

        self.reviews[review_id]["comments"].append({
            "comment": comment,
            "commenter": commenter,
            "timestamp": datetime.utcnow().isoformat()
        })
        return self.reviews[review_id]

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get a review by ID."""
        return self.reviews.get(review_id)
