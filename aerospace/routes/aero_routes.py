from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from aerospace.schemas.aero_schemas import AerospaceDesignRequest, AerospaceAnalysisResponse
from aerospace.services.aerodynamic_design_service import AerodynamicDesignService
from aerospace.models.aero_models import (
    AircraftProject, LiftAnalysis, DragAnalysis, WingLoadingAnalysis,
    StallSpeedAnalysis, AspectRatioAnalysis, PerformanceAnalysis
)
from aerospace.core.day5_8_integration import Day7ValidationEngine, Day8DocumentationEngine

router = APIRouter(prefix="/aerospace", tags=["Aerospace Preliminary Sizing"])

def get_db(): yield None # Mock DI

@router.post("/design", response_model=AerospaceAnalysisResponse, status_code=201)
async def run_full_aerodynamic_analysis(
    req: AerospaceDesignRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    NON-NEGOTIABLE WORKFLOW:
    Executes full preliminary sizing, enforces 11-step calculation transparency,
    validates via Day 7, and triggers Day 8 documentation.
    """
    try:
        aero_svc = AerodynamicDesignService()
        result = aero_svc.analyze(req)

        if not Day7ValidationEngine.validate_aerodynamics(
            req.aircraft_mass_kg, req.wing_area_m2, result.stall_speed_ms, req.cruise_velocity_ms, result.mach_number
        )["is_valid"]:
            raise HTTPException(status_code=400, detail=f"Validation Failed: {result.validation_warnings}")

        # Project Memory: Store all analyses
        project = AircraftProject(id=req.project_id, name=f"Aero_Project_{req.project_id}")
        # Note: In real app, fetch or create project. Mocked here for structure.
        
        if db is not None:
            db.add(LiftAnalysis(project_id=req.project_id, required_lift_n=result.weight_n, generated_lift_n=result.weight_n, lift_margin_percent=0.0, calculation_trace=[t.model_dump() for t in result.calculation_trace if "Lift" in t.step_name or "Weight" in t.step_name]))
            db.add(DragAnalysis(project_id=req.project_id, parasite_drag_n=result.cruise_drag_n * 0.7, induced_drag_n=result.cruise_drag_n * 0.3, total_drag_n=result.cruise_drag_n, calculation_trace=[t.model_dump() for t in result.calculation_trace if "Drag" in t.step_name]))
            db.add(WingLoadingAnalysis(project_id=req.project_id, wing_loading_n_m2=result.wing_loading_n_m2, classification="Moderate", calculation_trace=[t.model_dump() for t in result.calculation_trace if "Wing Loading" in t.step_name]))
            db.add(StallSpeedAnalysis(project_id=req.project_id, stall_speed_ms=result.stall_speed_ms, safe_flight_speed_ms=result.safe_flight_speed_ms, recommended_cruise_ms=req.cruise_velocity_ms, calculation_trace=[t.model_dump() for t in result.calculation_trace if "Stall" in t.step_name]))
            db.add(AspectRatioAnalysis(project_id=req.project_id, aspect_ratio=result.aspect_ratio, induced_drag_factor=result.cruise_cd - 0.02, efficiency_impact="Good", calculation_trace=[t.model_dump() for t in result.calculation_trace if "Aspect Ratio" in t.step_name]))
            db.add(PerformanceAnalysis(project_id=req.project_id, cruise_speed_ms=req.cruise_velocity_ms, power_required_w=result.power_required_w, mach_number=result.mach_number, calculation_trace=[t.model_dump() for t in result.calculation_trace if "Power" in t.step_name]))
            db.commit()

        # Day 8 Documentation Integration (Async)
        background_tasks.add_task(
            Day8DocumentationEngine.generate_aero_reports,
            project_id=req.project_id,
            data=result.model_dump()
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aerodynamic Orchestrator Failure: {str(e)}")


@router.get("/review-history")
async def get_review_history(project_id: int, db: Session = Depends(get_db)):
    """Retrieve past review decisions and lessons learned for a project."""
    # Mock implementation for structure
    return {"message": f"Review history for project {project_id} retrieved from Project Memory."}
