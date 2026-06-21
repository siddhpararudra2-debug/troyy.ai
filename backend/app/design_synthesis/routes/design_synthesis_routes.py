"""
Design Synthesis Routes
"""
import uuid
from datetime import datetime
from fastapi import APIRouter
from app.design_synthesis.schemas.schemas import (
    DesignSynthesisRequest,
    DesignSynthesisResponse,
    GeometrySynthesisRequest,
    GeometrySynthesisResponse,
    StructuralSizingRequest,
    StructuralSizingResponse,
    SynthesisValidationRequest,
    SynthesisValidationResponse,
)
from app.design_synthesis.services.requirement_parser import RequirementParser
from app.design_synthesis.services.geometry_synthesizer import GeometrySynthesizer
from app.design_synthesis.services.structural_sizing_engine import StructuralSizingEngine
from app.design_synthesis.services.synthesis_validator import SynthesisValidator


router = APIRouter(prefix="/design-synthesis", tags=["Design Synthesis"])
parser = RequirementParser()
synthesizer = GeometrySynthesizer()
sizer = StructuralSizingEngine()
validator = SynthesisValidator()


@router.post("/projects", response_model=DesignSynthesisResponse)
async def create_synthesis_project(request: DesignSynthesisRequest):
    """Create a new design synthesis project"""
    parsed_requirements = parser.parse(str(request.requirements))
    project_id = str(uuid.uuid4())
    
    return DesignSynthesisResponse(
        id=project_id,
        project_id=request.project_id,
        name=request.name,
        requirements={**request.requirements, **parsed_requirements},
        status="pending",
        current_iteration=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@router.post("/synthesize-geometry", response_model=GeometrySynthesisResponse)
async def synthesize_geometry(request: GeometrySynthesisRequest):
    """Synthesize geometry from requirements"""
    result = synthesizer.synthesize(request.requirements)
    return GeometrySynthesisResponse(
        id=result["id"],
        design_synthesis_project_id=request.design_synthesis_project_id,
        geometry=result["geometry"],
        parameters=result["parameters"],
        performance=result["performance"],
        status=result["status"],
        created_at=datetime.utcnow()
    )


@router.post("/size-structure", response_model=StructuralSizingResponse)
async def size_structure(request: StructuralSizingRequest):
    """Size a structural component"""
    result = sizer.size(request.loads, request.material)
    return StructuralSizingResponse(
        id=result["id"],
        design_synthesis_project_id=request.design_synthesis_project_id,
        dimensions=result["dimensions"],
        stress_analysis=result["stress_analysis"],
        safety_factor=result["stress_analysis"]["safety_factor"],
        mass_estimate=result["mass_estimate_kg"],
        created_at=datetime.utcnow()
    )


@router.post("/validate", response_model=SynthesisValidationResponse)
async def validate_synthesis(request: SynthesisValidationRequest):
    """Validate a synthesized design"""
    validation = validator.validate({})
    return SynthesisValidationResponse(
        id=validation["id"],
        design_synthesis_project_id=request.design_synthesis_project_id,
        is_valid=validation["is_valid"],
        issues=validation["issues"],
        recommendations=validation["recommendations"],
        created_at=datetime.utcnow()
    )
