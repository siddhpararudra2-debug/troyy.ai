"""
PCB Execution Routes
"""
from fastapi import APIRouter
from app.pcb_execution.schemas.schemas import (
    PCBExecutionProjectRequest,
    PCBExecutionProjectResponse,
    SchematicGenerationRequest,
    SchematicGenerationResponse,
    PCBLayoutRequest,
    PCBLayoutResponse,
    GerberExportRequest,
    GerberExportResponse,
)
from app.pcb_execution.services.pcb_orchestrator import PCBOrchestrator


router = APIRouter(prefix="/pcb-execution", tags=["PCB Execution"])
orchestrator = PCBOrchestrator()


@router.post("/projects", response_model=PCBExecutionProjectResponse)
async def create_pcb_project(request: PCBExecutionProjectRequest):
    """Create a new PCB execution project"""
    result = orchestrator.create_project(
        project_id=request.project_id,
        name=request.name,
        config=request.config
    )
    return PCBExecutionProjectResponse(**result)


@router.post("/schematics", response_model=SchematicGenerationResponse)
async def generate_schematic(request: SchematicGenerationRequest):
    """Generate a schematic"""
    result = orchestrator.generate_schematic(
        pcb_execution_project_id=request.pcb_execution_project_id,
        components=request.components,
        requirements=request.requirements
    )
    return SchematicGenerationResponse(**result)


@router.post("/layouts", response_model=PCBLayoutResponse)
async def generate_layout(request: PCBLayoutRequest):
    """Generate PCB layout"""
    result = orchestrator.generate_layout(
        pcb_execution_project_id=request.pcb_execution_project_id,
        schematic_id=request.schematic_id,
        board_width_mm=request.board_width_mm,
        board_height_mm=request.board_height_mm
    )
    return PCBLayoutResponse(**result)


@router.post("/gerber", response_model=GerberExportResponse)
async def export_gerber(request: GerberExportRequest):
    """Export Gerber files"""
    result = orchestrator.export_gerber(
        pcb_execution_project_id=request.pcb_execution_project_id,
        layout_id=request.layout_id
    )
    return GerberExportResponse(**result)
