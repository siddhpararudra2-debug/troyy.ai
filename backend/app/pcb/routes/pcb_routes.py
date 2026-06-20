"""
PCB Intelligence Routes
"""
from fastapi import APIRouter
from app.pcb.schemas.schemas import (
    PCBArchitectureRequest,
    PCBArchitectureResponse,
    PCBStackupRequest,
    PCBStackupResponse,
    PCBPlacementRequest,
    PCBPlacementResponse,
    PCBRoutingRequest,
    PCBRoutingResponse,
    PCBPowerRequest,
    PCBPowerResponse,
    PCBGroundingRequest,
    PCBGroundingResponse,
    PCBThermalRequest,
    PCBThermalResponse,
    PCBEMIRequest,
    PCBEMIResponse,
    PCBDRCRequest,
    PCBDRCResponse,
    PCBManufacturingRequest,
    PCBManufacturingResponse,
    PCBReviewRequest,
    PCBReviewResponse,
)
from app.pcb.services.pcb_architecture_service import PCBArchitectureService
from app.pcb.services.stackup_service import StackupService
from app.pcb.services.placement_service import PlacementService
from app.pcb.services.routing_service import RoutingService
from app.pcb.services.power_distribution_service import PowerDistributionService
from app.pcb.services.grounding_service import GroundingService
from app.pcb.services.thermal_service import ThermalService
from app.pcb.services.emi_emc_service import EMIEMCService
from app.pcb.services.drc_service import DRCService
from app.pcb.services.manufacturing_service import ManufacturingService
from app.pcb.services.pcb_review_service import PCBReviewService


router = APIRouter(prefix="/pcb", tags=["PCB Intelligence"])


@router.post("/architecture", response_model=PCBArchitectureResponse)
async def generate_architecture(request: PCBArchitectureRequest):
    return PCBArchitectureService.generate(request)


@router.post("/stackup", response_model=PCBStackupResponse)
async def generate_stackup(request: PCBStackupRequest):
    return StackupService.generate(request)


@router.post("/placement", response_model=PCBPlacementResponse)
async def generate_placement(request: PCBPlacementRequest):
    return PlacementService.generate(request)


@router.post("/routing", response_model=PCBRoutingResponse)
async def generate_routing(request: PCBRoutingRequest):
    return RoutingService.generate(request)


@router.post("/power", response_model=PCBPowerResponse)
async def generate_power(request: PCBPowerRequest):
    return PowerDistributionService.generate(request)


@router.post("/grounding", response_model=PCBGroundingResponse)
async def generate_grounding(request: PCBGroundingRequest):
    return GroundingService.generate(request)


@router.post("/thermal", response_model=PCBThermalResponse)
async def generate_thermal(request: PCBThermalRequest):
    return ThermalService.generate(request)


@router.post("/emi", response_model=PCBEMIResponse)
async def generate_emi(request: PCBEMIRequest):
    return EMIEMCService.generate(request)


@router.post("/drc", response_model=PCBDRCResponse)
async def generate_drc(request: PCBDRCRequest):
    return DRCService.generate(request)


@router.post("/manufacturing", response_model=PCBManufacturingResponse)
async def generate_manufacturing(request: PCBManufacturingRequest):
    return ManufacturingService.generate(request)


@router.post("/review", response_model=PCBReviewResponse)
async def generate_review(request: PCBReviewRequest):
    return PCBReviewService.generate(request)
