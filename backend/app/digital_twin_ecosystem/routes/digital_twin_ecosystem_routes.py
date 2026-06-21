"""
Digital Twin Ecosystem Routes
"""
from fastapi import APIRouter
from app.digital_twin_ecosystem.schemas.schemas import (
    DigitalTwinRequest,
    DigitalTwinResponse,
    TwinSyncRequest,
    TwinSyncResponse,
    TwinPredictionRequest,
    TwinPredictionResponse,
    TwinHealthRequest,
    TwinHealthResponse,
)
from app.digital_twin_ecosystem.services.twin_orchestrator import TwinOrchestrator
from app.digital_twin_ecosystem.services.twin_sync_service import TwinSyncService
from app.digital_twin_ecosystem.services.twin_prediction_engine import TwinPredictionEngine
from datetime import datetime

router = APIRouter(prefix="/digital-twin-ecosystem", tags=["Digital Twin Ecosystem"])
orchestrator = TwinOrchestrator()
sync_service = TwinSyncService()
prediction_engine = TwinPredictionEngine()


@router.post("/twins", response_model=DigitalTwinResponse)
async def create_digital_twin(request: DigitalTwinRequest):
    result = orchestrator.create_digital_twin(
        project_id=request.project_id,
        name=request.name,
        twin_type=request.twin_type,
        config=request.config
    )
    return DigitalTwinResponse(**result)


@router.post("/sync", response_model=TwinSyncResponse)
async def sync_digital_twin(request: TwinSyncRequest):
    result = sync_service.sync_twin(
        digital_twin_id=request.digital_twin_id,
        sensor_data=request.sensor_data
    )
    return TwinSyncResponse(**result)


@router.post("/predictions", response_model=TwinPredictionResponse)
async def get_prediction(request: TwinPredictionRequest):
    result = prediction_engine.predict(
        digital_twin_id=request.digital_twin_id,
        prediction_type=request.prediction_type
    )
    return TwinPredictionResponse(**result)


@router.post("/health", response_model=TwinHealthResponse)
async def get_health_report(request: TwinHealthRequest):
    return TwinHealthResponse(
        id=str(uuid.uuid4()),
        digital_twin_id=request.digital_twin_id,
        health_score=89.0,
        remaining_useful_life=240.0,  # hours
        recommendations=[{"type": "maintenance", "message": "Check motor bearings in 120 hours"}],
        created_at=datetime.utcnow()
    )
