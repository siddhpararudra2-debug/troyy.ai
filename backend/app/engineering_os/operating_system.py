"""
Engineering OS Control Center
Main entry point for all engineering OS functionality.
"""
import logging
from typing import Dict, Any, Optional

# Import all Sprint 8 modules
from app.agent_core.master_orchestrator import MasterOrchestrator
from app.autonomous_design.design_engine import DesignEngine
from app.knowledge_graph.graph_engine import GraphEngine
from app.copilot.engineering_copilot import EngineeringCopilot
from app.program_management.project_manager import ProjectManager
from app.analytics.performance_dashboard import PerformanceDashboard

logger = logging.getLogger(__name__)


class EngineeringOS:
    """
    Main Engineering OS class that orchestrates all functionality.
    """

    def __init__(
        self,
        agent_orchestrator: Optional[MasterOrchestrator] = None,
        design_engine: Optional[DesignEngine] = None,
        knowledge_graph: Optional[GraphEngine] = None,
        copilot: Optional[EngineeringCopilot] = None,
        project_manager: Optional[ProjectManager] = None,
        analytics: Optional[PerformanceDashboard] = None,
    ):
        self.agent_orchestrator = agent_orchestrator or MasterOrchestrator(None)
        self.design_engine = design_engine or DesignEngine()
        self.knowledge_graph = knowledge_graph or GraphEngine()
        self.copilot = copilot or EngineeringCopilot()
        self.project_manager = project_manager or ProjectManager()
        self.analytics = analytics or PerformanceDashboard()

        self._status = "ready"

    def get_status(self) -> Dict[str, Any]:
        return {
            "system_status": self._status,
            "components": [
                "agent_orchestrator",
                "design_engine",
                "knowledge_graph",
                "copilot",
                "project_manager",
                "analytics",
            ],
        }
