"""Operational Dashboard - Real-time operational monitoring."""

from typing import Dict, Any, List
from datetime import datetime


class OperationalDashboard:
    """Displays operational status and metrics."""
    
    def __init__(self):
        """Initialize operational dashboard."""
        self.dashboard_data: Dict[str, Any] = {}
        self.metrics_history: List[Dict[str, Any]] = []
    
    def update_dashboard(
        self,
        mission_metrics: Dict[str, Any],
        asset_metrics: Dict[str, Any],
        swarm_metrics: Dict[str, Any],
        operational_picture: Dict[str, Any]
    ) -> None:
        """Update dashboard with latest metrics."""
        self.dashboard_data = {
            "timestamp": datetime.utcnow(),
            "mission": mission_metrics,
            "assets": asset_metrics,
            "swarms": swarm_metrics,
            "operational_picture": operational_picture,
        }
        
        self.metrics_history.append(self.dashboard_data.copy())
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get current dashboard view."""
        return self.dashboard_data
    
    def get_mission_overview(self) -> Dict[str, Any]:
        """Get mission overview."""
        return self.dashboard_data.get("mission", {})
    
    def get_asset_overview(self) -> Dict[str, Any]:
        """Get asset overview."""
        return self.dashboard_data.get("assets", {})
    
    def get_swarm_overview(self) -> Dict[str, Any]:
        """Get swarm overview."""
        return self.dashboard_data.get("swarms", {})
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate operational report."""
        return {
            "report_time": datetime.utcnow(),
            "current_state": self.dashboard_data,
            "history_entries": len(self.metrics_history),
        }
