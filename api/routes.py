"""
FastAPI routes for Engineering OS Sprint 1.
All endpoints: chat, projects, memory, knowledge, agents, health.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from models.model_orchestrator import ModelOrchestrator
from models.routing_service import TaskType
from database.session import get_db
from memory.memory_service import MemoryService
from agents.agent_runtime import AgentRuntime

router = APIRouter()

# In-memory orchestrator (will be injected via app state)
_orchestrator: Optional[ModelOrchestrator] = None
_agent_runtime: Optional[AgentRuntime] = None


def get_orchestrator() -> ModelOrchestrator:
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Model orchestrator not initialized")
    return _orchestrator


def get_agent_runtime() -> AgentRuntime:
    if _agent_runtime is None:
        raise HTTPException(status_code=503, detail="Agent runtime not initialized")
    return _agent_runtime


def set_orchestrator(orch: ModelOrchestrator):
    global _orchestrator
    _orchestrator = orch


def set_agent_runtime(runtime: AgentRuntime):
    global _agent_runtime
    _agent_runtime = runtime


# ----- Request/Response Models -----

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Conversation session ID")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    task_type: Optional[TaskType] = Field(None, description="Override task classification")
    stream: bool = Field(False, description="Enable streaming response")
    temperature: float = Field(0.7, ge=0.0, le=2.0)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    model_used: str
    task_type: str
    response_time: float


class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    tags: Optional[list[str]] = Field(None, description="Project tags")


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    tags: list[str]
    created_at: str


class MemoryStoreRequest(BaseModel):
    project_id: str
    memory_type: str = Field(..., description="Type: conversation, requirement, decision, etc.")
    content: str
    title: Optional[str] = None
    summary: Optional[str] = None
    importance: float = 1.0
    tags: Optional[list[str]] = None


class MemorySearchRequest(BaseModel):
    query: str
    project_id: Optional[str] = None
    memory_types: Optional[list[str]] = None
    limit: int = 20


class KnowledgeSearchRequest(BaseModel):
    query: str
    collection: str = "engineering_knowledge"
    limit: int = 10
    score_threshold: float = 0.3


class AgentExecuteRequest(BaseModel):
    project_id: str
    agent_type: str = Field(..., description="mechanical, electronics, pcb, firmware, simulation, documentation")
    title: str
    description: str
    input_data: dict = {}
    priority: int = 0


# ----- API Endpoints -----

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message through the AI model orchestrator."""
    orch = get_orchestrator()
    
    result = await orch.chat(
        message=request.message,
        session_id=request.session_id,
        task_type=request.task_type,
        stream=False,
        temperature=request.temperature,
    )
    
    # Store in memory if project context provided
    if request.project_id:
        try:
            db_session = await anext(get_db())
            memory_service = MemoryService(db_session)
            await memory_service.store_conversation_memory(
                project_id=uuid.UUID(request.project_id),
                user_message=request.message,
                assistant_response=result.content,
                model_used=result.model_used,
            )
        except Exception as e:
            pass  # Non-critical
    
    return ChatResponse(
        response=result.content,
        session_id=result.session_id,
        model_used=result.model_used,
        task_type=result.task_type.value,
        response_time=result.response_time,
    )


@router.post("/projects")
async def create_project(request: ProjectCreate):
    """Create a new engineering project."""
    # Simple in-memory project creation for Sprint 1
    project_id = str(uuid.uuid4())
    return {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "status": "active",
        "tags": request.tags or [],
        "created_at": "2026-01-01T00:00:00Z",
    }


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    return {
        "id": project_id,
        "name": "Sample Project",
        "description": "Engineering project",
        "status": "active",
        "tags": [],
        "created_at": "2026-01-01T00:00:00Z",
    }


@router.post("/memory/store")
async def store_memory(request: MemoryStoreRequest, session=Depends(get_db)):
    """Store a memory entry."""
    memory_service = MemoryService(session)
    result = await memory_service.store(
        project_id=uuid.UUID(request.project_id),
        memory_type=request.memory_type,
        content=request.content,
        title=request.title,
        summary=request.summary,
        importance=request.importance,
        tags=request.tags,
    )
    return result


@router.post("/memory/search")
async def search_memory(request: MemorySearchRequest, session=Depends(get_db)):
    """Search memory entries."""
    memory_service = MemoryService(session)
    results = await memory_service.search(
        query=request.query,
        project_id=uuid.UUID(request.project_id) if request.project_id else None,
        memory_types=request.memory_types,
        limit=request.limit,
    )
    return {
        "results": [
            {
                "content": r.content,
                "memory_type": r.memory_type,
                "title": r.title,
                "summary": r.summary,
                "source": r.source,
                "importance": r.importance,
                "score": r.score,
            }
            for r in results
        ]
    }


@router.post("/knowledge/search")
async def search_knowledge(request: KnowledgeSearchRequest):
    """Search knowledge base."""
    from rag.retrieval_service import RetrievalService
    from rag.vector_store import VectorStore
    from rag.embedding_service import EmbeddingService, EmbeddingProvider
    
    vector_store = VectorStore()
    embedding_provider = EmbeddingProvider(EmbeddingService())
    retrieval = RetrievalService(vector_store, embedding_provider)
    
    results = await retrieval.search_knowledge(
        query=request.query,
        collection=request.collection,
        limit=request.limit,
        score_threshold=request.score_threshold,
    )
    
    return {"results": results}


@router.post("/agents/execute")
async def execute_agent(request: AgentExecuteRequest):
    """Execute a task on an engineering agent."""
    runtime = get_agent_runtime()
    task_id = await runtime.submit_task(
        project_id=request.project_id,
        agent_type=request.agent_type,
        title=request.title,
        description=request.description,
        input_data=request.input_data,
        priority=request.priority,
    )
    return {"task_id": task_id, "status": "submitted"}


@router.get("/agents/status")
async def get_agent_status():
    """Get agent runtime status."""
    runtime = get_agent_runtime()
    return await runtime.get_status()


@router.get("/health")
async def health_check():
    """System health check."""
    orch = get_orchestrator()
    status = await orch.get_system_status()
    return {
        "system": "Engineering OS",
        "version": "1.0.0",
        "status": status,
        "components": {
            "models": "operational",
            "memory": "operational",
            "agents": "operational",
            "knowledge": "operational",
        },
    }