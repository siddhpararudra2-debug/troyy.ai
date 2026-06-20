import pytest
from aerospace.schemas.aero_schemas import AerospaceDesignRequest
from aerospace.services.aerodynamic_design_service import AerodynamicDesignService

def test_aerodynamic_analysis_success():
    """Test successful aerodynamic analysis and verification of outputs."""
    req = AerospaceDesignRequest(
        project_id=1,
        aircraft_mass_kg=25.0,
        wing_area_m2=1.5,
        wingspan_m=3.0,
        cl_max=1.4,
        cd0=0.035,
        oswald_efficiency=0.85,
        cruise_velocity_ms=25.0,
        altitude_m=0.0
    )
    
    svc = AerodynamicDesignService()
    result = svc.analyze(req)
    
    # 1. Check Weight
    assert abs(result.weight_n - (25.0 * 9.80665)) < 0.1
    
    # 2. Check Aspect Ratio: b^2 / S = 9 / 1.5 = 6.0
    assert abs(result.aspect_ratio - 6.0) < 0.01
    
    # 3. Check Stall Speed: sqrt(2 * 245.16 / (1.225 * 1.5 * 1.4)) = sqrt(490.32 / 2.5725) = sqrt(190.6) = 13.8 m/s
    assert abs(result.stall_speed_ms - 13.8) < 0.5
    
    # 4. Verify 11-step transparency rule is enforced
    assert len(result.calculation_trace) >= 6 # At least 6 major steps recorded
    for step in result.calculation_trace:
        assert step.requirement != ""
        assert step.formula_selection != ""
        assert step.unit_analysis != ""
        assert step.substitution != ""
        assert step.engineering_interpretation != ""

def test_mach_number_validation_warning():
    """Ensures high-speed designs trigger compressibility warnings."""
    req = AerospaceDesignRequest(
        project_id=2,
        aircraft_mass_kg=50.0,
        wing_area_m2=1.0,
        wingspan_m=2.0,
        cl_max=1.2,
        cd0=0.03,
        oswald_efficiency=0.8,
        cruise_velocity_ms=120.0, # High speed
        altitude_m=0.0
    )
    
    svc = AerodynamicDesignService()
    result = svc.analyze(req)
    
    assert result.mach_number > 0.3
    assert any("CRITICAL" in w and "Mach number" in w for w in result.validation_warnings)
