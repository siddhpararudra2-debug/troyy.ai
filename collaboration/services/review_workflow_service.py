import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime
from collaboration.schemas.collab_models import ReviewRecord, Comment, Approval
from collaboration.schemas.enums import ReviewStatus

class ReviewWorkflowService:
    """State machine for engineering review workflows.
    Transitions: DRAFT → PENDING_REVIEW → IN_REVIEW → APPROVED|REJECTED|REQUIRES_CHANGES"""
    
    VALID_TRANSITIONS = {
        ReviewStatus.DRAFT: [ReviewStatus.PENDING_REVIEW],
        ReviewStatus.PENDING_REVIEW: [ReviewStatus.IN_REVIEW, ReviewStatus.DRAFT],
        ReviewStatus.IN_REVIEW: [ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.REQUIRES_CHANGES],
        ReviewStatus.REQUIRES_CHANGES: [ReviewStatus.PENDING_REVIEW],
        ReviewStatus.APPROVED: [],  # Terminal
        ReviewStatus.REJECTED: [ReviewStatus.DRAFT],  # Can restart
    }
    
    def __init__(self):
        self.reviews: Dict[str, ReviewRecord] = {}
        
    def create_review(self, workspace_id: str, artifact_type: str, artifact_ref: str,
                     title: str, requester_id: str, reviewer_ids: List[str],
                     description: str = "") -> ReviewRecord:
        # Compute hash of artifact for immutable audit trail
        artifact_hash = hashlib.sha256(
            json.dumps({"type": artifact_type, "ref": artifact_ref, "title": title}, sort_keys=True).encode()
        ).hexdigest()
        
        review = ReviewRecord(
            workspace_id=workspace_id,
            artifact_type=artifact_type,
            artifact_ref=artifact_ref,
            title=title,
            description=description,
            requester_id=requester_id,
            reviewers=reviewer_ids,
            sha256_hash=artifact_hash,
            status=ReviewStatus.DRAFT
        )
        self.reviews[review.id] = review
        return review
        
    def transition(self, review_id: str, new_status: ReviewStatus, actor_id: str) -> ReviewRecord:
        review = self.reviews.get(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
            
        if new_status not in self.VALID_TRANSITIONS[review.status]:
            raise ValueError(f"Invalid transition: {review.status} → {new_status}")
            
        # Actor validation
        if new_status == ReviewStatus.PENDING_REVIEW and actor_id != review.requester_id:
            raise PermissionError("Only requester can submit for review")
        if new_status in [ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.REQUIRES_CHANGES]:
            if actor_id not in review.reviewers:
                raise PermissionError("Only assigned reviewers can make decisions")
                
        review.status = new_status
        review.updated_at = datetime.utcnow()
        review.decisions.append({
            "actor_id": actor_id,
            "new_status": new_status.value,
            "timestamp": datetime.utcnow().isoformat()
        })
        return review
        
    def add_comment(self, review_id: str, author_id: str, content: str,
                   parent_id: Optional[str] = None, mentions: List[str] = None) -> Comment:
        review = self.reviews.get(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
            
        comment = Comment(
            review_id=review_id,
            author_id=author_id,
            content=content,
            parent_id=parent_id,
            mentions=mentions or []
        )
        review.comments.append(comment.model_dump())
        review.updated_at = datetime.utcnow()
        return comment
        
    def get_review(self, review_id: str) -> Optional[ReviewRecord]:
        return self.reviews.get(review_id)
        
    def list_reviews(self, workspace_id: Optional[str] = None,
                    status: Optional[ReviewStatus] = None) -> List[ReviewRecord]:
        reviews = list(self.reviews.values())
        if workspace_id:
            reviews = [r for r in reviews if r.workspace_id == workspace_id]
        if status:
            reviews = [r for r in reviews if r.status == status]
        return reviews
