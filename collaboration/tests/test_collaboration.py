import pytest
from collaboration.services.workspace_service import WorkspaceService
from collaboration.services.review_workflow_service import ReviewWorkflowService
from collaboration.services.permissions_service import PermissionsService
from collaboration.services.approval_service import ApprovalService
from collaboration.schemas.enums import Role, ReviewStatus, Permission

def test_permissions():
    svc = PermissionsService()
    assert svc.has_permission(Role.CHIEF_ENGINEER, Permission.APPROVE)
    assert not svc.has_permission(Role.VIEWER, Permission.WRITE)
    assert not svc.has_permission(Role.MECHANICAL_ENGINEER, Permission.APPROVE)

def test_workspace_creation():
    svc = WorkspaceService()
    user = svc.register_user("alice", "alice@example.com", Role.CHIEF_ENGINEER)
    ws = svc.create_workspace("VTOL Project", "PROJ-001", user.id)
    assert ws.name == "VTOL Project"
    assert ws.project_id == "PROJ-001"
    assert len(svc.activity_log) == 1

def test_review_workflow():
    ws_svc = WorkspaceService()
    review_svc = ReviewWorkflowService()
    
    user = ws_svc.register_user("bob", "bob@example.com", Role.MECHANICAL_ENGINEER)
    reviewer = ws_svc.register_user("carol", "carol@example.com", Role.CHIEF_ENGINEER)
    ws = ws_svc.create_workspace("Test", "P1", user.id)
    
    review = review_svc.create_review(ws.id, "DESIGN", "CAD-001", "Wing Design",
                                      user.id, [reviewer.id])
    assert review.status == ReviewStatus.DRAFT
    
    # Submit for review
    review_svc.transition(review.id, ReviewStatus.PENDING_REVIEW, user.id)
    assert review.status == ReviewStatus.PENDING_REVIEW
    
    # Start review
    review_svc.transition(review.id, ReviewStatus.IN_REVIEW, reviewer.id)
    assert review.status == ReviewStatus.IN_REVIEW
    
    # Approve
    review_svc.transition(review.id, ReviewStatus.APPROVED, reviewer.id)
    assert review.status == ReviewStatus.APPROVED

def test_invalid_transition():
    review_svc = ReviewWorkflowService()
    ws_svc = WorkspaceService()
    user = ws_svc.register_user("dave", "dave@example.com", Role.MECHANICAL_ENGINEER)
    ws = ws_svc.create_workspace("Test", "P1", user.id)
    review = review_svc.create_review(ws.id, "DESIGN", "CAD-002", "Test", user.id, [])
    
    # Can't approve a draft directly
    with pytest.raises(ValueError, match="Invalid transition"):
        review_svc.transition(review.id, ReviewStatus.APPROVED, user.id)

def test_approval_signature():
    ws_svc = WorkspaceService()
    review_svc = ReviewWorkflowService()
    perm_svc = PermissionsService()
    approval_svc = ApprovalService(perm_svc, review_svc)
    
    user = ws_svc.register_user("eve", "eve@example.com", Role.MECHANICAL_ENGINEER)
    chief = ws_svc.register_user("frank", "frank@example.com", Role.CHIEF_ENGINEER)
    ws = ws_svc.create_workspace("Test", "P1", user.id)
    review = review_svc.create_review(ws.id, "DESIGN", "CAD-003", "Test", user.id, [chief.id])
    review_svc.transition(review.id, ReviewStatus.PENDING_REVIEW, user.id)
    review_svc.transition(review.id, ReviewStatus.IN_REVIEW, chief.id)
    
    approval = approval_svc.grant_approval(review.id, chief.id, Role.CHIEF_ENGINEER,
                                           "APPROVED", "Meets all requirements")
    assert len(approval.signature_hash) == 64
    assert review.status == ReviewStatus.APPROVED

def test_approval_requires_permission():
    ws_svc = WorkspaceService()
    review_svc = ReviewWorkflowService()
    perm_svc = PermissionsService()
    approval_svc = ApprovalService(perm_svc, review_svc)
    
    user = ws_svc.register_user("grace", "grace@example.com", Role.MECHANICAL_ENGINEER)
    viewer = ws_svc.register_user("hank", "hank@example.com", Role.VIEWER)
    ws = ws_svc.create_workspace("Test", "P1", user.id)
    review = review_svc.create_review(ws.id, "DESIGN", "CAD-004", "Test", user.id, [viewer.id])
    review_svc.transition(review.id, ReviewStatus.PENDING_REVIEW, user.id)
    review_svc.transition(review.id, ReviewStatus.IN_REVIEW, viewer.id)
    
    with pytest.raises(PermissionError):
        approval_svc.grant_approval(review.id, viewer.id, Role.VIEWER,
                                   "APPROVED", "Should fail")
