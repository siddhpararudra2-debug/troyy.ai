"""
CAD Execution Routes
"""
from fastapi import APIRouter
from app.cad_execution.schemas.schemas import (
    CADExecutionProjectRequest,
    CADExecutionProjectResponse,
    CADPartExecutionRequest,
    CADPartExecutionResponse,
    CADAssemblyExecutionRequest,
    CADAssemblyExecutionResponse,
    CADExportRequest,
    CADExportResponse,
    CADValidationRequest,
    CADValidationResponse,
)
from app.cad_execution.services.cad_orchestrator import CADOrchestrator


router = APIRouter(prefix="/cad-execution", tags=["CAD Execution"])
orchestrator = CADOrchestrator()


@router.post("/projects", response_model=CADExecutionProjectResponse)
async def create_cad_project(request: CADExecutionProjectRequest):
    """Create a new CAD execution project"""
    result = orchestrator.create_project(
        project_id=request.project_id,
        name=request.name,
        engine=request.engine,
        config=request.config
    )
    return CADExecutionProjectResponse(**result)


@router.post("/parts", response_model=CADPartExecutionResponse)
async def generate_cad_part(request: CADPartExecutionRequest):
    """Generate a CAD part"""
    result = orchestrator.generate_part(
        cad_execution_project_id=request.cad_execution_project_id,
        part_name=request.part_name,
        part_type=request.part_type,
        parametric_dimensions=request.parametric_dimensions,
        material=request.material
    )
    return CADPartExecutionResponse(**result)


@router.post("/assemblies", response_model=CADAssemblyExecutionResponse)
async def generate_cad_assembly(request: CADAssemblyExecutionRequest):
    """Generate a CAD assembly"""
    result = orchestrator.generate_assembly(
        cad_execution_project_id=request.cad_execution_project_id,
        assembly_name=request.assembly_name,
        parts=request.parts,
        mates=request.mates
    )
    return CADAssemblyExecutionResponse(**result)


@router.post("/exports", response_model=CADExportResponse)
async def export_cad(request: CADExportRequest):
    """Export a CAD model"""
    result = orchestrator.export(
        cad_execution_project_id=request.cad_execution_project_id,
        part_or_assembly_id=request.part_or_assembly_id,
        export_format=request.export_format
    )
    return CADExportResponse(**result)


@router.post("/validate", response_model=CADValidationResponse)
async def validate_cad(request: CADValidationRequest):
    """Validate a CAD model"""
    result = orchestrator.validate(
        cad_execution_project_id=request.cad_execution_project_id,
        part_or_assembly_id=request.part_or_assembly_id,
        validation_type=request.validation_type
    )
    return CADValidationResponse(**result)
