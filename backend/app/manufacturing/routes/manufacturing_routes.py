"""
Manufacturing Intelligence Platform API Routes
"""
from fastapi import APIRouter
from app.manufacturing.schemas.schemas import (
    BOMRequest,
    BOMResponse,
    CostEstimateRequest,
    CostEstimateResponse,
    SourcingRequest,
    SourcingResponse,
    CNCPlanRequest,
    CNCPlanResponse,
    PrintPlanRequest,
    PrintPlanResponse,
    ProcurementPlanRequest,
    ProcurementPlanResponse,
    ProductionRouteRequest,
    ProductionRouteResponse,
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    BuildPackageRequest,
    BuildPackageResponse
)
from app.manufacturing.services.bom_generation_service import BOMGenerationService
from app.manufacturing.services.sourcing_service import SourcingService
from app.manufacturing.services.cost_estimation_service import CostEstimationService
from app.manufacturing.services.cnc_planning_service import CNCPlanningService
from app.manufacturing.services.additive_manufacturing_service import AdditiveManufacturingService
from app.manufacturing.services.procurement_service import ProcurementService
from app.manufacturing.services.production_route_service import ProductionRouteService
from app.manufacturing.services.manufacturing_risk_service import ManufacturingRiskService
from app.manufacturing.services.build_package_service import BuildPackageService


router = APIRouter(prefix="/manufacturing", tags=["Manufacturing Intelligence Platform"])


@router.post("/bom", response_model=BOMResponse)
async def generate_bom(request: BOMRequest):
    return BOMGenerationService.generate(request)


@router.post("/cost", response_model=CostEstimateResponse)
async def estimate_cost(request: CostEstimateRequest):
    return CostEstimationService.estimate(request)


@router.post("/sourcing", response_model=SourcingResponse)
async def source_components(request: SourcingRequest):
    return SourcingService.analyze(request)


@router.post("/cnc", response_model=CNCPlanResponse)
async def plan_cnc(request: CNCPlanRequest):
    return CNCPlanningService.plan(request)


@router.post("/printing", response_model=PrintPlanResponse)
async def plan_printing(request: PrintPlanRequest):
    return AdditiveManufacturingService.plan(request)


@router.post("/procurement", response_model=ProcurementPlanResponse)
async def plan_procurement(request: ProcurementPlanRequest):
    return ProcurementService.plan(request)


@router.post("/production-route", response_model=ProductionRouteResponse)
async def generate_production_route(request: ProductionRouteRequest):
    return ProductionRouteService.generate(request)


@router.post("/risk", response_model=RiskAssessmentResponse)
async def assess_risks(request: RiskAssessmentRequest):
    return ManufacturingRiskService.analyze(request)


@router.post("/build-package", response_model=BuildPackageResponse)
async def generate_build_package(request: BuildPackageRequest):
    return BuildPackageService.generate(request)
