from pydantic import BaseModel, Field
from typing import List, Optional
from aerospace.core.day5_8_integration import AeroCalculationStep

class AerospaceDesignRequest(BaseModel):
    project_id: int
    aircraft_mass_kg: float = Field(..., gt=0, description="Total aircraft mass in kg")
    wing_area_m2: float = Field(..., gt=0, description="Wing reference area in m²")
    wingspan_m: float = Field(..., gt=0, description="Wingspan in meters")
    cl_max: float = Field(..., gt=0, description="Maximum lift coefficient (e.g., 1.2 to 1.8)")
    cd0: float = Field(..., gt=0, description="Zero-lift (parasite) drag coefficient")
    oswald_efficiency: float = Field(..., gt=0, le=1.0, description="Oswald efficiency factor (e), typically 0.7-0.9")
    cruise_velocity_ms: float = Field(..., gt=0, description="Target cruise velocity in m/s")
    altitude_m: float = Field(default=0.0, ge=0, description="Operating altitude in meters")

class AerospaceAnalysisResponse(BaseModel):
    project_id: int
    weight_n: float
    air_density_kg_m3: float
    aspect_ratio: float
    wing_loading_n_m2: float
    stall_speed_ms: float
    safe_flight_speed_ms: float
    cruise_cl: float
    cruise_cd: float
    cruise_drag_n: float
    power_required_w: float
    mach_number: float
    calculation_trace: List[AeroCalculationStep]
    validation_warnings: List[str]
