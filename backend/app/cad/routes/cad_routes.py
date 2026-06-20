"""
CAD Generation & Engineering Geometry Routes
"""
from fastapi import APIRouter
from app.cad.schemas.schemas import (
    CADPartRequest, CADPartResponse,
    CADAassemblyRequest, CADAassemblyResponse,
    CADDrawingRequest, CADDrawingResponse,
    CADToleranceRequest, CADToleranceResponse,
    CADManufacturingRequest, CADManufacturingResponse,
    CADReviewRequest, CADReviewResponse,
)
from app.cad.services.cad_generation_service import CADGenerationService
from app.cad.services.assembly_generation_service import AssemblyGenerationService
from app.cad.services.drawing_generation_service import DrawingGenerationService
from app.cad.services.tolerance_service import ToleranceService
from app.cad.services.manufacturing_geometry_service import ManufacturingGeometryService
from app.cad.services.cad_review_service import CADReviewService


router = APIRouter(prefix="/cad", tags=["CAD Generation & Geometry"])


@router.post("/generate", response_model=CADPartResponse)
async def generate_cad_part(request: CADPartRequest):
    return CADGenerationService.generate_part(request)


@router.post("/assembly", response_model=CADAassemblyResponse)
async def generate_cad_assembly(request: CADAassemblyRequest):
    return AssemblyGenerationService.generate(request)


@router.post("/drawing", response_model=CADDrawingResponse)
async def generate_cad_drawing(request: CADDrawingRequest):
    return DrawingGenerationService.generate(request)


@router.post("/tolerance", response_model=CADToleranceResponse)
async def analyze_tolerances(request: CADToleranceRequest):
    return ToleranceService.analyze(request)


@router.post("/manufacturing", response_model=CADManufacturingResponse)
async def analyze_manufacturing(request: CADManufacturingRequest):
    return ManufacturingGeometryService.analyze(request)


@router.post("/review", response_model=CADReviewResponse)
async def review_cad(request: CADReviewRequest):
    return CADReviewService.review(request)
