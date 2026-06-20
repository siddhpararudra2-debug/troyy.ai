"""
Engineering Knowledge Graph & Memory Platform Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseKnowledgeRequest(BaseModel):
    project_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class KnowledgeNodeRequest(BaseKnowledgeRequest):
    node_type: str
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeNodeResponse(BaseModel):
    id: str
    node_type: str
    name: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class KnowledgeRelationshipRequest(BaseKnowledgeRequest):
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeRelationshipResponse(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Dict[str, Any]
    created_at: datetime


class KnowledgeGraphResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    nodes: List[KnowledgeNodeResponse]
    relationships: List[KnowledgeRelationshipResponse]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class EngineeringMemoryRequest(BaseKnowledgeRequest):
    memory_type: str
    title: str
    content: str
    tags: Optional[List[str]] = Field(default_factory=list)


class EngineeringMemoryResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    memory_type: str
    title: str
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class EngineeringSearchRequest(BaseModel):
    query: str
    search_type: str = "semantic"
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    limit: int = 10


class EngineeringSearchResult(BaseModel):
    id: str
    type: str
    title: str
    summary: str
    score: float
    metadata: Dict[str, Any]
    created_at: datetime


class EngineeringSearchResponse(BaseModel):
    results: List[EngineeringSearchResult]
    execution_time_ms: Optional[float] = None


class RAGRequest(BaseModel):
    query: str
    context_type: str = "all"
    limit: int = 5


class RAGResponse(BaseModel):
    query: str
    context_pack: List[Dict[str, Any]]
    references: List[str]
    execution_time_ms: Optional[float] = None
    created_at: datetime


class FailureRecordRequest(BaseKnowledgeRequest):
    failure_type: str
    title: str
    description: str
    root_cause: Optional[str] = None
    symptoms: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)


class FailureRecordResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    failure_type: str
    title: str
    description: str
    root_cause: Optional[str] = None
    symptoms: List[str]
    mitigations: List[str]
    created_at: datetime


class LessonLearnedRequest(BaseKnowledgeRequest):
    title: str
    description: str
    impact: str
    tags: List[str] = Field(default_factory=list)


class LessonLearnedResponse(BaseModel):
    id: str
    project_id: Optional[str] = None
    title: str
    description: str
    impact: str
    tags: List[str]
    created_at: datetime
