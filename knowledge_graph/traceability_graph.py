"""
Traceability Graph - Full-system traceability through the knowledge graph.

Capabilities:
- Full Traceability Mapping
- Traceability Impact Analysis
- Coverage Reports
"""

from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from knowledge_graph.graph_builder import KnowledgeGraph


class TraceabilityGraph:
    """Provides full traceability analysis through the knowledge graph."""

    def __init__(self, knowledge_graph: KnowledgeGraph):
        self._graph = knowledge_graph

    def trace_from_requirement(self, req_name: str) -> Dict[str, Any]:
        """Trace a requirement through design, implementation, and verification."""
        path = []
        req_nodes = [n for n in self._graph._nodes.values()
                     if n.domain == "requirements" and req_name.lower() in n.name.lower()]
        for req_node in req_nodes:
            connected = self._graph.get_connected_nodes(req_node.id)
            path.append({"requirement": req_node.to_dict(), "trace_to": [n.to_dict() for n in connected]})
        return {"trace_paths": path, "total": len(path)}

    def coverage_report(self) -> Dict[str, Any]:
        """Generate traceability coverage report across all domains."""
        domains = set(n.domain for n in self._graph._nodes.values())
        report = {}
        for domain in domains:
            nodes = [n for n in self._graph._nodes.values() if n.domain == domain]
            linked = sum(1 for n in nodes if len(self._graph.get_connected_nodes(n.id)) > 0)
            report[domain] = {"total": len(nodes), "traced": linked,
                             "untraced": len(nodes) - linked,
                             "coverage_pct": round(linked / len(nodes) * 100, 1) if nodes else 0}
        return {"report": report, "generated_at": datetime.utcnow().isoformat()}

    def verify_traceability(self) -> Dict[str, Any]:
        """Verify that all artifacts have proper traceability."""
        issues = []
        for node in self._graph._nodes.values():
            connections = self._graph.get_connected_nodes(node.id)
            if not connections:
                issues.append({
                    "node": node.to_dict(),
                    "issue": "No traceability connections",
                    "domain": node.domain,
                })
        return {"issues": issues, "total_issues": len(issues),
                "fully_traced": len(issues) == 0}