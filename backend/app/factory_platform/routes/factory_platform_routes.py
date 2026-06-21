"""
Factory Platform Routes
"""
from fastapi import APIRouter
from app.factory_platform.schemas.schemas import ProductionRunRequest, WorkOrderRequest
from app.factory_platform.services.factory_orchestrator import FactoryOrchestrator
from app.factory_platform.services.work_order_service import WorkOrderService

router = APIRouter(prefix="/factory", tags=["Factory Platform"])
factory_orch = FactoryOrchestrator()
wo_service = WorkOrderService()


@router.post("/production")
async def start_production(request: ProductionRunRequest):
    result = factory_orch.execute_production_run(request.product_id, request.quantity)
    return result


@router.post("/order")
async def create_work_order(request: WorkOrderRequest):
    result = wo_service.create_work_order(request.product_id, request.quantity, request.due_date)
    return result


@router.get("/report/{id}")
async def get_production_report(id: str):
    return {"report_id": id, "status": "ready"}
