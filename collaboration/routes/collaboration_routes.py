from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from collaboration.schemas.collab_models import Workspace, ReviewRecord, Comment, Approval
from collaboration.schemas.enums import Role, ReviewStatus, NotificationType
from collaboration.services.workspace_service import WorkspaceService
from collaboration.services.review_workflow_service import ReviewWorkflowService
from collaboration.services.permissions_service import PermissionsService
from collaboration.services.approval_service import ApprovalService
from collaboration.services.notification_service import NotificationService
from collaboration.services.activity_feed_service import ActivityFeedService

router = APIRouter(prefix="/collaboration", tags=["Enterprise Collaboration Platform"])

# Service instances (in production, these would be injected via DI)
workspace_svc = WorkspaceService()
review_svc = ReviewWorkflowService()
permissions_svc = PermissionsService()
approval_svc = ApprovalService(permissions_svc, review_svc)
notification_svc = NotificationService()
activity_svc = ActivityFeedService(workspace_svc)

@router.post("/workspace", response_model=Workspace)
async def create_workspace(name: str, project_id: str, creator_id: str):
    return workspace_svc.create_workspace(name, project_id, creator_id)

@router.get("/workspaces")
async def list_workspaces(project_id: Optional[str] = None):
    return [w.model_dump() for w in workspace_svc.list_workspaces(project_id)]

@router.post("/team")
async def create_team(name: str, lead_id: str, member_ids: List[str]):
    return workspace_svc.create_team(name, lead_id, member_ids).model_dump()

@router.post("/user")
async def register_user(username: str, email: str, role: Role):
    return workspace_svc.register_user(username, email, role).model_dump()

@router.post("/review", response_model=ReviewRecord)
async def create_review(workspace_id: str, artifact_type: str, artifact_ref: str,
                       title: str, requester_id: str, reviewer_ids: List[str],
                       description: str = ""):
    review = review_svc.create_review(workspace_id, artifact_type, artifact_ref,
                                      title, requester_id, reviewer_ids, description)
    # Notify reviewers
    for rid in reviewer_ids:
        notification_svc.send(rid, NotificationType.REVIEW_REQUESTED,
                             f"Review requested: {title}",
                             f"You have been assigned to review '{title}'",
                             f"/reviews/{review.id}")
    return review

@router.post("/review/{review_id}/transition")
async def transition_review(review_id: str, new_status: ReviewStatus, actor_id: str):
    try:
        return review_svc.transition(review_id, new_status, actor_id).model_dump()
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/review/{review_id}/comment", response_model=Comment)
async def add_comment(review_id: str, author_id: str, content: str,
                     parent_id: Optional[str] = None, mentions: List[str] = None):
    comment = review_svc.add_comment(review_id, author_id, content, parent_id, mentions)
    # Notify mentioned users
    for mentioned_id in (mentions or []):
        notification_svc.send(mentioned_id, NotificationType.MENTION,
                             "You were mentioned in a review",
                             f"{author_id} mentioned you in a comment",
                             f"/reviews/{review_id}")
    return comment

@router.post("/review/{review_id}/approve")
async def approve_review(review_id: str, approver_id: str, approver_role: Role,
                        decision: str, justification: str):
    try:
        approval = approval_svc.grant_approval(review_id, approver_id, approver_role,
                                               decision, justification)
        # Notify requester
        review = review_svc.get_review(review_id)
        notification_svc.send(review.requester_id, NotificationType.APPROVAL_GRANTED,
                             f"Review {decision.lower()}",
                             f"Your review '{review.title}' was {decision.lower()}",
                             f"/reviews/{review_id}")
        return approval.model_dump()
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/review/{review_id}")
async def get_review(review_id: str):
    review = review_svc.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review.model_dump()

@router.get("/reviews")
async def list_reviews(workspace_id: Optional[str] = None, status: Optional[ReviewStatus] = None):
    return [r.model_dump() for r in review_svc.list_reviews(workspace_id, status)]

@router.get("/activity/{workspace_id}")
async def get_activity_feed(workspace_id: str, limit: int = 50):
    return [e.model_dump() for e in activity_svc.get_feed(workspace_id, limit)]

@router.get("/notifications/{user_id}")
async def get_notifications(user_id: str, unread_only: bool = False):
    if unread_only:
        return [n.model_dump() for n in notification_svc.get_unread(user_id)]
    return [n.model_dump() for n in notification_svc.get_all(user_id)]
