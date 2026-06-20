"""
Engineering Knowledge Graph & Memory Platform API Routes
"""
from fastapi import APIRouter
from app.knowledge.schemas.schemas import (
    KnowledgeNodeRequest,
    KnowledgeNodeResponse,
    KnowledgeRelationshipRequest,
    KnowledgeRelationshipResponse,
    KnowledgeGraphResponse,
    EngineeringMemoryRequest,
    EngineeringMemoryResponse,
    EngineeringSearchRequest,
    EngineeringSearchResponse,
    RAGRequest,
    RAGResponse,
    FailureRecordRequest,
    FailureRecordResponse,
    LessonLearnedRequest,
    LessonLearnedResponse
)
from app.knowledge.services.knowledge_graph_service import KnowledgeGraphService
from app.knowledge.services.engineering_memory_service import EngineeringMemoryService
from app.knowledge.services.rag_service import RAGService
from app.knowledge.services.engineering_search_service import EngineeringSearchService
from app.knowledge.services.failure_analysis_service import FailureAnalysisService
from app.knowledge.services.lessons_learned_service import LessonsLearnedService


router = APIRouter(prefix="/knowledge", tags=["Engineering Knowledge Graph & Memory Platform"])


@router.post("/graph/node", response_model=KnowledgeNodeResponse)
async def create_knowledge_node(request: KnowledgeNodeRequest):
    return KnowledgeGraphService.create_node(request)


@router.post("/graph/relationship", response_model=KnowledgeRelationshipResponse)
async def create_knowledge_relationship(request: KnowledgeRelationshipRequest):
    return KnowledgeGraphService.create_relationship(request)


@router.get("/graph/project/{project_id}", response_model=KnowledgeGraphResponse)
async def get_project_knowledge_graph(project_id: str):
    return KnowledgeGraphService.get_graph(project_id)


@router.post("/memory", response_model=EngineeringMemoryResponse)
async def store_engineering_memory(request: EngineeringMemoryRequest):
    return EngineeringMemoryService.store(request)


@router.post("/search", response_model=EngineeringSearchResponse)
async def search_knowledge(request: EngineeringSearchRequest):
    return EngineeringSearchService.search(request)


@router.post("/rag", response_model=RAGResponse)
async def retrieve_rag_context(request: RAGRequest):
    return RAGService.retrieve(request)


@router.post("/failure", response_model=FailureRecordResponse)
async def record_failure(request: FailureRecordRequest):
    return FailureAnalysisService.record(request)


@router.post("/lessons", response_model=LessonLearnedResponse)
async def record_lesson_learned(request: LessonLearnedRequest):
    return LessonsLearnedService.record(request)
