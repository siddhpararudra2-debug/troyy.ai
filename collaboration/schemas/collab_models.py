from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from collaboration.schemas.enums import Role, ReviewStatus, Permission, NotificationType

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: Role
    team_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    members: List[str] = Field(default_factory=list)  # user IDs
    lead_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Workspace(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    project_id: str
    team_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReviewRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str
    artifact_type: str  # "DESIGN", "SCHEMATIC", "SIMULATION", "CODE"
    artifact_ref: str
    title: str
    description: str = ""
    status: ReviewStatus = ReviewStatus.DRAFT
    requester_id: str
    reviewers: List[str] = Field(default_factory=list)
    comments: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sha256_hash: Optional[str] = None  # Immutable audit trail

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str
    author_id: str
    content: str
    parent_id: Optional[str] = None  # For threaded replies
    mentions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Approval(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    review_id: str
    approver_id: str
    decision: str  # "APPROVED", "REJECTED", "CONDITIONAL"
    justification: str
    signature_hash: str  # Cryptographic signature
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ActivityEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str
    user_id: str
    event_type: str
    entity_type: str
    entity_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    link: Optional[str] = None
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
