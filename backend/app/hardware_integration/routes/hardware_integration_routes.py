"""
Hardware Integration Routes
"""
from fastapi import APIRouter
from app.hardware_integration.schemas.schemas import HardwareConnectRequest, HardwareConnectResponse, HardwareTestRequest
from app.hardware_integration.services.hardware_orchestrator import HardwareOrchestrator
from app.hardware_integration.services.hardware_test_service import HardwareTestService

router = APIRouter(prefix="/hardware", tags=["Hardware Integration"])
hw_orchestrator = HardwareOrchestrator()
hw_test_service = HardwareTestService()


@router.post("/connect", response_model=HardwareConnectResponse)
async def connect_hardware(request: HardwareConnectRequest):
    result = hw_orchestrator.connect_hardware(request.device_type, request.connection_params)
    return HardwareConnectResponse(**result)


@router.post("/test")
async def test_hardware(request: HardwareTestRequest):
    result = hw_test_service.run_test(request.device_id, request.test_type)
    return result
