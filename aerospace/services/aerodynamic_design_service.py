import math
from aerospace.schemas.aero_schemas import AerospaceDesignRequest, AerospaceAnalysisResponse
from aerospace.core.day5_8_integration import Day5CalculationCore, Day7ValidationEngine

class AerodynamicDesignService:
    GRAVITY = 9.80665
    SEA_LEVEL_DENSITY = 1.225
    SPEED_OF_SOUND_SEA_LEVEL = 340.3

    def _get_air_density(self, altitude_m: float) -> float:
        # International Standard Atmosphere (ISA) approximation
        return self.SEA_LEVEL_DENSITY * ((1 - 2.25577e-5 * altitude_m) ** 4.25588)

    def analyze(self, req: AerospaceDesignRequest) -> AerospaceAnalysisResponse:
        trace = []
        
        # 1. Weight Calculation
        weight_n = req.aircraft_mass_kg * self.GRAVITY
        trace.append(Day5CalculationCore.record(
            step_name="Aircraft Weight",
            requirement="Determine total gravitational force acting on the aircraft.",
            assumption="Standard Earth gravity applies.",
            formula_selection="W = m × g",
            formula_explanation="Weight equals mass multiplied by gravitational acceleration.",
            unit_analysis="[kg] × [m/s²] = [N] (Newtons)",
            substitution=f"{req.aircraft_mass_kg} kg × {self.GRAVITY} m/s²",
            intermediate_calculations=f"{req.aircraft_mass_kg} × {self.GRAVITY}",
            final_result=weight_n,
            unit="N",
            engineering_interpretation="This is the baseline force that lift must counteract in steady, level flight."
        ))

        # 2. Air Density
        rho = self._get_air_density(req.altitude_m)
        trace.append(Day5CalculationCore.record(
            step_name="Air Density",
            requirement="Determine atmospheric density at operating altitude.",
            assumption="International Standard Atmosphere (ISA) model applies.",
            formula_selection="ρ = ρ₀ × (1 - 2.25577e-5 × h)^4.25588",
            formula_explanation="Density decreases with altitude based on the barometric formula.",
            unit_analysis="[kg/m³] × [dimensionless] = [kg/m³]",
            substitution=f"1.225 × (1 - 2.25577e-5 × {req.altitude_m})^4.25588",
            intermediate_calculations=f"1.225 × ({1 - 2.25577e-5 * req.altitude_m})^4.25588",
            final_result=rho,
            unit="kg/m³",
            engineering_interpretation="Lower density at altitude reduces both lift and drag proportionally."
        ))

        # 3. Aspect Ratio
        ar = (req.wingspan_m ** 2) / req.wing_area_m2
        trace.append(Day5CalculationCore.record(
            step_name="Aspect Ratio",
            requirement="Evaluate wing slenderness to estimate induced drag efficiency.",
            assumption="Wing is roughly rectangular or tapered with standard planform.",
            formula_selection="AR = b² / S",
            formula_explanation="Aspect ratio is the square of the wingspan divided by the wing area.",
            unit_analysis="[m]² / [m²] = [dimensionless]",
            substitution=f"({req.wingspan_m})² / {req.wing_area_m2}",
            intermediate_calculations=f"{req.wingspan_m ** 2} / {req.wing_area_m2}",
            final_result=ar,
            unit="dimensionless",
            engineering_interpretation="Higher AR reduces induced drag but increases structural weight and reduces roll rate."
        ))

        # 4. Wing Loading
        wl = weight_n / req.wing_area_m2
        classification = "Low (Good for slow flight/STOL)" if wl < 500 else ("Moderate (General Aviation)" if wl < 1500 else "High (Fast/Jet)")
        trace.append(Day5CalculationCore.record(
            step_name="Wing Loading",
            requirement="Determine the load supported by each unit of wing area.",
            assumption="Weight is evenly distributed across the reference area.",
            formula_selection="WL = W / S",
            formula_explanation="Wing loading is total weight divided by wing reference area.",
            unit_analysis="[N] / [m²] = [N/m²]",
            substitution=f"{weight_n:.2f} N / {req.wing_area_m2} m²",
            intermediate_calculations=f"{weight_n:.2f} / {req.wing_area_m2}",
            final_result=wl,
            unit="N/m²",
            engineering_interpretation=f"Classified as {classification}. Lower values improve turn rate and reduce stall speed."
        ))

        # 5. Stall Speed
        vs = math.sqrt((2 * weight_n) / (rho * req.wing_area_m2 * req.cl_max))
        safe_speed = vs * 1.3
        trace.append(Day5CalculationCore.record(
            step_name="Stall Speed",
            requirement="Determine the minimum steady flight speed.",
            assumption="1G, unaccelerated, sea-level or specified altitude flight. Clean configuration.",
            formula_selection="Vs = √(2W / (ρ × S × Cl_max))",
            formula_explanation="Stall occurs when the wing can no longer generate enough lift at maximum Cl.",
            unit_analysis="√([N] / ([kg/m³] × [m²] × [dimensionless])) = √([kg·m/s²] / [kg/m·s²]) = [m/s]",
            substitution=f"√(2 × {weight_n:.2f} / ({rho:.4f} × {req.wing_area_m2} × {req.cl_max}))",
            intermediate_calculations=f"√({2 * weight_n:.2f} / {rho * req.wing_area_m2 * req.cl_max:.4f})",
            final_result=vs,
            unit="m/s",
            engineering_interpretation=f"Safe flight speed (1.3 Vs) is {safe_speed:.2f} m/s. Never operate below this in steady flight."
        ))

        # 6. Cruise Lift Coefficient
        cl_cruise = (2 * weight_n) / (rho * (req.cruise_velocity_ms ** 2) * req.wing_area_m2)
        trace.append(Day5CalculationCore.record(
            step_name="Cruise Lift Coefficient",
            requirement="Determine the Cl required to maintain level flight at cruise speed.",
            assumption="Steady, level, unaccelerated flight (Lift = Weight).",
            formula_selection="Cl = 2W / (ρ × V² × S)",
            formula_explanation="Rearranging the lift equation to solve for the required coefficient of lift.",
            unit_analysis="[N] / ([kg/m³] × [m/s]² × [m²]) = [dimensionless]",
            substitution=f"(2 × {weight_n:.2f}) / ({rho:.4f} × {req.cruise_velocity_ms}² × {req.wing_area_m2})",
            intermediate_calculations=f"{2 * weight_n:.2f} / {rho * (req.cruise_velocity_ms ** 2) * req.wing_area_m2:.4f}",
            final_result=cl_cruise,
            unit="dimensionless",
            engineering_interpretation="This Cl must be significantly lower than Cl_max to ensure a safe cruise margin."
        ))

        # 7. Cruise Drag
        cd_induced = (cl_cruise ** 2) / (math.pi * ar * req.oswald_efficiency)
        cd_total = req.cd0 + cd_induced
        drag_n = 0.5 * rho * (req.cruise_velocity_ms ** 2) * req.wing_area_m2 * cd_total
        trace.append(Day5CalculationCore.record(
            step_name="Cruise Drag",
            requirement="Determine total aerodynamic resistance at cruise speed.",
            assumption="Drag polar is parabolic: Cd = Cd0 + Cl²/(π·AR·e).",
            formula_selection="D = 0.5 × ρ × V² × S × (Cd0 + Cl²/(π·AR·e))",
            formula_explanation="Total drag is the sum of parasite drag and induced drag.",
            unit_analysis="[kg/m³] × [m/s]² × [m²] × [dimensionless] = [N]",
            substitution=f"0.5 × {rho:.4f} × {req.cruise_velocity_ms}² × {req.wing_area_m2} × ({req.cd0} + {cl_cruise:.4f}²/(π × {ar:.2f} × {req.oswald_efficiency}))",
            intermediate_calculations=f"Cd_induced = {cd_induced:.4f}, Cd_total = {cd_total:.4f}",
            final_result=drag_n,
            unit="N",
            engineering_interpretation="This is the thrust required from the propulsion system to maintain cruise speed."
        ))

        # 8. Performance (Power Required)
        power_req = drag_n * req.cruise_velocity_ms
        trace.append(Day5CalculationCore.record(
            step_name="Power Required",
            requirement="Determine the mechanical power needed to overcome drag at cruise.",
            assumption="Propulsive efficiency is not yet factored (this is aerodynamic power required).",
            formula_selection="P_req = D × V",
            formula_explanation="Power is the product of drag force and velocity.",
            unit_analysis="[N] × [m/s] = [J/s] = [W] (Watts)",
            substitution=f"{drag_n:.2f} N × {req.cruise_velocity_ms} m/s",
            intermediate_calculations=f"{drag_n:.2f} × {req.cruise_velocity_ms}",
            final_result=power_req,
            unit="W",
            engineering_interpretation="Divide by propeller efficiency (e.g., 0.8) to find the required shaft power from the motor/engine."
        ))

        # 9. Mach Number Check
        speed_of_sound = self.SPEED_OF_SOUND_SEA_LEVEL * math.sqrt(max(0, 1 - 2.25577e-5 * req.altitude_m))
        mach = req.cruise_velocity_ms / speed_of_sound
        
        # Validation (Day 7)
        validation = Day7ValidationEngine.validate_aerodynamics(
            mass_kg=req.aircraft_mass_kg,
            wing_area=req.wing_area_m2,
            stall_speed=vs,
            cruise_speed=req.cruise_velocity_ms,
            mach_number=mach
        )

        return AerospaceAnalysisResponse(
            project_id=req.project_id,
            weight_n=round(weight_n, 2),
            air_density_kg_m3=round(rho, 4),
            aspect_ratio=round(ar, 2),
            wing_loading_n_m2=round(wl, 2),
            stall_speed_ms=round(vs, 2),
            safe_flight_speed_ms=round(safe_speed, 2),
            cruise_cl=round(cl_cruise, 4),
            cruise_cd=round(cd_total, 4),
            cruise_drag_n=round(drag_n, 2),
            power_required_w=round(power_req, 2),
            mach_number=round(mach, 3),
            calculation_trace=trace,
            validation_warnings=validation["warnings"]
        )
