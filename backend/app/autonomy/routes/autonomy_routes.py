"""
Autonomy Routes
"""
from fastapi import APIRouter
from app.autonomy.schemas.schemas import ControlRequest, MissionRequest
from app.autonomy.services.control_system_service import ControlSystemService
from app.autonomy.services.mission_autonomy_service import MissionAutonomyService

router = APIRouter(prefix="/autonomy", tags=["Autonomy"])
ctrl_service = ControlSystemService()
mission_service = MissionAutonomyService()


@router.post("/control")
async def design_control(request: ControlRequest):
    result = ctrl_service.design_controller(request.type, request.parameters)
    return result


@router.post("/mission")
async def create_mission(request: MissionRequest):
    result = mission_service.create_mission(request.waypoints)
    return result


@router.get("/report/{id}")
async def get_autonomy_report(id: str):
    return {"report_id": id, "status": "ready"}
