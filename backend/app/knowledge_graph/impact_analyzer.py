"""
Impact Analyzer for Engineering Knowledge Graph
Analyzes impact of changes to one entity on other entities.
"""
import logging
from typing import Dict, Any, List
from app.knowledge_graph.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Analyzes impact of a change to one node on the rest of the graph.
    """

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        self.dependency_analyzer = dependency_analyzer

    def analyze_change_impact(self, node_id: str) -> Dict[str, Any]:
        """
        Analyze impact of changing the given node.
        """
        dependents = self.dependency_analyzer.find_dependents(node_id)
        all_impacted = self.dependency_analyzer.find_all_dependencies_recursive(node_id)

        impact_level = "low"
        if len(dependents) > 10:
            impact_level = "high"
        elif len(dependents) > 3:
            impact_level = "medium"

        return {
            "changed_node": node_id,
            "direct_dependents": dependents,
            "all_impacted": list(all_impacted),
            "impact_level": impact_level,
            "recommendations": [
                "Review all impacted components before making changes",
                "Consider running validation on affected areas",
            ],
        }
