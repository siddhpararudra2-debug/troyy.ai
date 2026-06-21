"""
Predictive Engineering Routes
"""
from fastapi import APIRouter
from app.predictive_engineering.schemas.schemas import (
    PredictiveAnalysisRequest,
    PredictiveAnalysisResponse,
    AnomalyRequest,
    AnomalyResponse,
    MaintenanceRequest,
    MaintenanceResponse,
)
from app.predictive_engineering.services.predictive_engine import PredictiveEngine
from app.predictive_engineering.services.anomaly_detector import AnomalyDetector
from app.predictive_engineering.services.maintenance_planner import MaintenancePlanner

router = APIRouter(prefix="/predictive-engineering", tags=["Predictive Engineering"])
engine = PredictiveEngine()
detector = AnomalyDetector()
planner = MaintenancePlanner()


@router.post("/analyze", response_model=PredictiveAnalysisResponse)
async def run_analysis(request: PredictiveAnalysisRequest):
    result = engine.analyze(
        project_id=request.project_id,
        analysis_type=request.analysis_type,
        data=request.data
    )
    return PredictiveAnalysisResponse(**result)


@router.post("/anomalies", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest):
    result = detector.detect(
        predictive_analysis_id=request.predictive_analysis_id,
        sensor_data=request.sensor_data
    )
    return AnomalyResponse(**result)


@router.post("/maintenance", response_model=MaintenanceResponse)
async def generate_plan(request: MaintenanceRequest):
    result = planner.plan(request.predictive_analysis_id)
    return MaintenanceResponse(**result)
