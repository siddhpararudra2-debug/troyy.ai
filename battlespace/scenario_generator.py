"""Scenario Generator - Creates operational scenarios."""

from typing import Dict, List, Any
import uuid
from datetime import datetime


class ScenarioGenerator:
    """Generates operational scenarios."""
    
    def __init__(self):
        """Initialize scenario generator."""
        self.scenarios: Dict[str, Dict[str, Any]] = {}
    
    def create_scenario(
        self,
        name: str,
        scenario_type: str,
        environment_id: str,
        initial_conditions: Dict[str, Any]
    ) -> str:
        """Create new scenario."""
        scenario_id = str(uuid.uuid4())
        
        self.scenarios[scenario_id] = {
            "id": scenario_id,
            "name": name,
            "type": scenario_type,
            "environment_id": environment_id,
            "initial_conditions": initial_conditions,
            "created_at": datetime.utcnow(),
            "events": [],
        }
        
        return scenario_id
    
    def add_event(
        self,
        scenario_id: str,
        event_type: str,
        time_offset: float,
        parameters: Dict[str, Any]
    ) -> bool:
        """Add event to scenario."""
        if scenario_id not in self.scenarios:
            return False
        
        event = {
            "type": event_type,
            "time": time_offset,
            "parameters": parameters,
        }
        
        self.scenarios[scenario_id]["events"].append(event)
        return True
    
    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Retrieve scenario."""
        return self.scenarios.get(scenario_id, {})
    
    def list_scenarios(self, scenario_type: str = None) -> List[Dict[str, Any]]:
        """List scenarios."""
        scenarios = list(self.scenarios.values())
        
        if scenario_type:
            scenarios = [s for s in scenarios if s["type"] == scenario_type]
        
        return scenarios
