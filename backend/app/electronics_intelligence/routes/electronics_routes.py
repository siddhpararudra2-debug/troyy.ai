"""
Electronics Intelligence Routes
FastAPI routes for the Electronics Intelligence Platform.
"""

from fastapi import APIRouter
from app.electronics_intelligence.schemas.schemas import (
    ComponentRecommendationRequest,
    ComponentRecommendationResponse,
    MicrocontrollerSelectionRequest,
    MicrocontrollerSelectionResponse,
    SensorSelectionRequest,
    SensorSelectionResponse,
    RegulatorSelectionRequest,
    RegulatorSelectionResponse,
    MosfetSelectionRequest,
    MosfetSelectionResponse,
    CommunicationSelectionRequest,
    CommunicationSelectionResponse,
    CompatibilityAnalysisRequest,
    CompatibilityAnalysisResponse,
    ElectronicsArchitectureRequest,
    ElectronicsArchitectureResponse,
)
from app.electronics_intelligence.services.component_recommendation_service import (
    ComponentRecommendationService,
)
from app.electronics_intelligence.services.microcontroller_service import (
    MicrocontrollerSelectionService,
)
from app.electronics_intelligence.services.sensor_selection_service import (
    SensorSelectionService,
)
from app.electronics_intelligence.services.regulator_selection_service import (
    RegulatorSelectionService,
)
from app.electronics_intelligence.services.mosfet_selection_service import (
    MosfetSelectionService,
)
from app.electronics_intelligence.services.communication_selection_service import (
    CommunicationSelectionService,
)
from app.electronics_intelligence.services.compatibility_service import (
    CompatibilityService,
)
from app.electronics_intelligence.services.architecture_service import (
    ArchitectureService,
)

router = APIRouter(prefix="/electronics", tags=["Electronics Intelligence"])


@router.post("/components", response_model=ComponentRecommendationResponse)
async def recommend_components(
    request: ComponentRecommendationRequest,
):
    """Recommend electronic components based on requirements."""
    return ComponentRecommendationService.recommend(request)


@router.post("/microcontroller", response_model=MicrocontrollerSelectionResponse)
async def select_microcontroller(
    request: MicrocontrollerSelectionRequest,
):
    """Select a microcontroller based on requirements."""
    return MicrocontrollerSelectionService.select(request)


@router.post("/sensors", response_model=SensorSelectionResponse)
async def select_sensor(
    request: SensorSelectionRequest,
):
    """Select a sensor based on type and requirements."""
    return SensorSelectionService.select(request)


@router.post("/regulators", response_model=RegulatorSelectionResponse)
async def select_regulator(
    request: RegulatorSelectionRequest,
):
    """Select a voltage regulator based on type and requirements."""
    return RegulatorSelectionService.select(request)


@router.post("/mosfets", response_model=MosfetSelectionResponse)
async def select_mosfet(
    request: MosfetSelectionRequest,
):
    """Select a MOSFET based on requirements."""
    return MosfetSelectionService.select(request)


@router.post("/communications", response_model=CommunicationSelectionResponse)
async def select_communication(
    request: CommunicationSelectionRequest,
):
    """Select a communication protocol based on requirements."""
    return CommunicationSelectionService.select(request)


@router.post("/compatibility", response_model=CompatibilityAnalysisResponse)
async def analyze_compatibility(
    request: CompatibilityAnalysisRequest,
):
    """Analyze compatibility between selected components."""
    return CompatibilityService.analyze(request)


@router.post("/architecture", response_model=ElectronicsArchitectureResponse)
async def generate_architecture(
    request: ElectronicsArchitectureRequest,
):
    """Generate electronics architecture (power, signal, communication, subsystems)."""
    return ArchitectureService.generate(request)
