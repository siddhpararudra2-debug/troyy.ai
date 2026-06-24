"""Sprint 17 API Routes: Engineering Governance, Configuration Management, etc."""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
import uuid

router = APIRouter(prefix="/api/sprint17", tags=["Sprint 17 - Governance"])

# Configuration Management
@router.post("/configuration/baseline")
async def create_baseline(
    project_id: str,
    name: str,
    description: Optional[str] = None
):
    from configuration import BaselineManager
    manager = BaselineManager()
    return manager.create_baseline(project_id, name, description)

@router.post("/configuration/release")
async def create_release(
    project_id: str,
    name: str,
    version: str
):
    from configuration import ReleaseManager
    manager = ReleaseManager()
    return manager.create_release(project_id, name, version)

# Workflow Engine
@router.post("/workflow/create")
async def create_workflow(
    project_id: str,
    name: str,
    definition: Dict[str, Any],
    workflow_type: Optional[str] = None
):
    from workflow import WorkflowEngine
    engine = WorkflowEngine()
    return engine.create_workflow(project_id, name, definition, workflow_type)

@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    from workflow import WorkflowEngine
    engine = WorkflowEngine()
    workflow = engine.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(404, detail="Workflow not found")
    return workflow

# Review & Approval
@router.post("/review/create")
async def create_review(
    project_id: str,
    artifact_id: str,
    title: str,
    description: Optional[str] = None
):
    from reviews import ReviewManager
    manager = ReviewManager()
    return manager.create_review(project_id, artifact_id, title, description)

@router.post("/approval/request")
async def request_approval(
    review_id: str,
    approval_type: str
):
    from reviews import ApprovalManager
    manager = ApprovalManager()
    return manager.request_approval(review_id, approval_type)

# Knowledge Base
@router.post("/knowledge/lesson")
async def add_lesson(
    project_id: str,
    title: str,
    lesson: str
):
    from personal_knowledge import LessonsLearnedManager
    manager = LessonsLearnedManager()
    return manager.add_lesson(project_id, title, lesson)

@router.post("/journal/entry")
async def add_journal_entry(
    project_id: str,
    content: str,
    entry_type: Optional[str] = "note"
):
    from personal_knowledge import EngineeringJournal
    journal = EngineeringJournal()
    return journal.add_entry(project_id, content, entry_type)

# Backup & Recovery
@router.post("/backup/create")
async def create_backup(
    name: str,
    description: Optional[str] = None
):
    from backup import PostgresBackup
    backup = PostgresBackup()
    return backup.create_backup(name, description)

# Health Check
@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "sprint17"}
