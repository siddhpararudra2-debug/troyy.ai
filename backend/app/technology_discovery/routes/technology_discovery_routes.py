"""
Technology Discovery Routes
"""
from fastapi import APIRouter
from app.technology_discovery.schemas.schemas import (
    DiscoveryRequest,
    DiscoveryResponse,
    TrendForecastRequest,
    TrendForecastResponse,
    TechDashboardResponse
)
from app.technology_discovery.services.discovery_orchestrator import DiscoveryOrchestrator
from app.technology_discovery.services.trend_forecasting_service import TrendForecastingService
from app.technology_discovery.services.technology_dashboard import TechnologyDashboard

router = APIRouter(prefix="/technology", tags=["Technology Discovery"])

discovery_orchestrator = DiscoveryOrchestrator()
trend_service = TrendForecastingService()
dashboard_service = TechnologyDashboard()


@router.post("/discovery", response_model=DiscoveryResponse)
async def run_discovery(request: DiscoveryRequest):
    result = discovery_orchestrator.run_discovery(request.domain)
    return DiscoveryResponse(**result)


@router.post("/forecast", response_model=TrendForecastResponse)
async def forecast_trends(request: TrendForecastRequest):
    result = trend_service.forecast_trends(request.domain, request.horizon)
    return TrendForecastResponse(**result)


@router.get("/dashboard", response_model=TechDashboardResponse)
async def get_tech_dashboard():
    result = dashboard_service.get_dashboard()
    return TechDashboardResponse(**result)
