import time
from advanced_simulation.schemas.engineering_report import ReportContext, EngineeringReport

class DigitalTwinService:
    def __init__(self):
        self.twins = {}

    def update_state(self, twin_id: str, state: dict) -> EngineeringReport:
        with ReportContext(
            requirements=["Update digital twin state and maintain historical telemetry"],
            assumptions=["State updates are sequential and time-stamped"],
            constraints=["Memory limits for history buffer"],
            formula_selection="Time-Series State Appending",
            formula_explanation="Maintains an in-memory ring buffer of state variables for real-time tracking.",
            unit_analysis="State variables in native engineering units."
        ) as ctx:
            if twin_id not in self.twins:
                self.twins[twin_id] = {"history": [], "current_state": {}}
                
            twin = self.twins[twin_id]
            twin["current_state"] = state
            twin["history"].append({"timestamp": time.time(), "state": state})
            
            # Keep only last 1000 states to prevent memory leaks
            if len(twin["history"]) > 1000:
                twin["history"] = twin["history"][-1000:]
                
            ctx.finalize(
                final_results={"twin_id": twin_id, "current_state": state, "history_length": len(twin["history"])},
                interpretation=f"Digital twin '{twin_id}' updated. History length: {len(twin['history'])}."
            )
        return ctx.report
