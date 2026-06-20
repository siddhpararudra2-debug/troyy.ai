"""
System Integration & Hardware-Software Co-Design Routes
"""
from fastapi import APIRouter
from app.system_integration.schemas.schemas import (
    SystemArchitectureRequest, SystemArchitectureResponse,
    TraceabilityRequest, TraceabilityResponse,
    IntegrationRequest, IntegrationResponse,
    HardwareSoftwareMappingRequest, HardwareSoftwareMappingResponse,
    InterfaceManagementRequest, InterfaceManagementResponse,
    DependencyManagementRequest, DependencyManagementResponse,
    DigitalThreadRequest, DigitalThreadResponse,
    ConfigurationManagementRequest, ConfigurationManagementResponse,
    SystemValidationRequest, SystemValidationResponse,
    SystemReviewRequest, SystemReviewResponse,
)
from app.system_integration.services.system_architecture_service import SystemArchitectureService
from app.system_integration.services.requirement_traceability_service import RequirementTraceabilityService
from app.system_integration.services.subsystem_integration_service import SubsystemIntegrationService
from app.system_integration.services.hardware_software_mapping_service import HardwareSoftwareMappingService
from app.system_integration.services.interface_management_service import InterfaceManagementService
from app.system_integration.services.dependency_management_service import DependencyManagementService
from app.system_integration.services.digital_thread_service import DigitalThreadService
from app.system_integration.services.configuration_management_service import ConfigurationManagementService
from app.system_integration.services.system_validation_service import SystemValidationService
from app.system_integration.services.integration_review_service import IntegrationReviewService


router = APIRouter(prefix="/system", tags=["System Integration & Co-Design"])


@router.post("/architecture", response_model=SystemArchitectureResponse)
async def generate_system_architecture(request: SystemArchitectureRequest):
    return SystemArchitectureService.generate(request)


@router.post("/traceability", response_model=TraceabilityResponse)
async def analyze_traceability(request: TraceabilityRequest):
    return RequirementTraceabilityService.analyze(request)


@router.post("/integration", response_model=IntegrationResponse)
async def integrate_subsystems(request: IntegrationRequest):
    return SubsystemIntegrationService.integrate(request)


@router.post("/interfaces", response_model=InterfaceManagementResponse)
async def manage_interfaces(request: InterfaceManagementRequest):
    return InterfaceManagementService.manage(request)


@router.post("/dependencies", response_model=DependencyManagementResponse)
async def analyze_dependencies(request: DependencyManagementRequest):
    return DependencyManagementService.analyze(request)


@router.post("/digital-thread", response_model=DigitalThreadResponse)
async def build_digital_thread(request: DigitalThreadRequest):
    return DigitalThreadService.build(request)


@router.post("/configuration", response_model=ConfigurationManagementResponse)
async def manage_configuration(request: ConfigurationManagementRequest):
    return ConfigurationManagementService.manage(request)


@router.post("/validation", response_model=SystemValidationResponse)
async def validate_system(request: SystemValidationRequest):
    return SystemValidationService.validate(request)


@router.post("/review", response_model=SystemReviewResponse)
async def review_system(request: SystemReviewRequest):
    return IntegrationReviewService.review(request)
