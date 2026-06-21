"""
PCB Execution Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class PCBExecutionProjectRequest(BaseModel):
    project_id: str
    name: str
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PCBExecutionProjectResponse(BaseModel):
    id: str
    project_id: str
    name: str
    status: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class SchematicGenerationRequest(BaseModel):
    pcb_execution_project_id: str
    components: List[Dict[str, Any]] = Field(default_factory=list)
    requirements: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SchematicGenerationResponse(BaseModel):
    id: str
    pcb_execution_project_id: str
    components: List[Dict[str, Any]]
    nets: List[Dict[str, Any]]
    status: str
    file_path: Optional[str] = None
    created_at: datetime


class PCBLayoutRequest(BaseModel):
    pcb_execution_project_id: str
    schematic_id: str
    board_width_mm: float = 100.0
    board_height_mm: float = 80.0


class PCBLayoutResponse(BaseModel):
    id: str
    pcb_execution_project_id: str
    schematic_id: str
    board_width_mm: float
    board_height_mm: float
    placement: Dict[str, Any]
    routing: Dict[str, Any]
    status: str
    file_path: Optional[str] = None
    created_at: datetime


class GerberExportRequest(BaseModel):
    pcb_execution_project_id: str
    layout_id: str


class GerberExportResponse(BaseModel):
    id: str
    pcb_execution_project_id: str
    layout_id: str
    files: List[Dict[str, Any]]
    status: str
    created_at: datetime
