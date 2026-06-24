"""
Traceability Engine - Requirements traceability and impact analysis.

Capabilities:
- Requirement Traceability
- Impact Analysis
- Coverage Analysis
- Traceability Reports
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any, Set, Tuple
from datetime import datetime

from requirements.requirement_manager import Requirement, RequirementManager


class TraceLinkType(str, Enum):
    """Types of traceability links."""
    DERIVES = "derives"
    REFINES = "refines"
    SATISFIES = "satisfies"
    VERIFIES = "verifies"
    ALLOCATES = "allocates"
    CONSTRAINS = "constrains"
    TRACES = "traces"
    DEPENDS = "depends"
    CONFLICTS = "conflicts"


class TraceLinkDirection(str, Enum):
    """Direction of traceability."""
    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"


class TraceLink:
    """A traceability link between engineering artifacts."""

    def __init__(
        self,
        link_id: str,
        source_id: str,
        target_id: str,
        link_type: TraceLinkType = TraceLinkType.TRACES,
        source_type: str = "requirement",
        target_type: str = "requirement",
        description: Optional[str] = None,
        direction: TraceLinkDirection = TraceLinkDirection.BIDIRECTIONAL,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = link_id
        self.source_id = source_id
        self.target_id = target_id
        self.link_type = link_type
        self.source_type = source_type
        self.target_type = target_type
        self.description = description
        self.direction = direction
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "link_type": self.link_type.value,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "description": self.description,
            "direction": self.direction.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class TraceabilityEngine:
    """
    Manages traceability between requirements, architecture, design, and verification.
    Provides impact analysis and coverage reporting.
    """

    def __init__(self, requirement_manager: Optional[RequirementManager] = None):
        self._links: Dict[str, TraceLink] = {}
        self._requirement_manager = requirement_manager or RequirementManager()

    def set_requirement_manager(self, manager: RequirementManager):
        """Set the requirement manager."""
        self._requirement_manager = manager

    def add_link(
        self,
        source_id: str,
        target_id: str,
        link_type: TraceLinkType = TraceLinkType.TRACES,
        source_type: str = "requirement",
        target_type: str = "requirement",
        description: Optional[str] = None,
        direction: TraceLinkDirection = TraceLinkDirection.BIDIRECTIONAL,
    ) -> TraceLink:
        """Create a traceability link between two artifacts."""
        link_id = str(uuid.uuid4())
        link = TraceLink(
            link_id=link_id,
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            source_type=source_type,
            target_type=target_type,
            description=description,
            direction=direction,
        )
        self._links[link_id] = link
        return link

    def remove_link(self, link_id: str) -> bool:
        """Remove a traceability link."""
        if link_id in self._links:
            del self._links[link_id]
            return True
        return False

    def get_links_for(self, artifact_id: str) -> List[TraceLink]:
        """Get all traceability links for an artifact."""
        return [
            link for link in self._links.values()
            if link.source_id == artifact_id or link.target_id == artifact_id
        ]

    def get_upstream_traceability(self, artifact_id: str) -> List[TraceLink]:
        """Get all upstream (parent/source) traceability links."""
        return [link for link in self._links.values() if link.target_id == artifact_id]

    def get_downstream_traceability(self, artifact_id: str) -> List[TraceLink]:
        """Get all downstream (child/target) traceability links."""
        return [link for link in self._links.values() if link.source_id == artifact_id]

    def trace_forward(self, artifact_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Forward traceability analysis - find all downstream items."""
        result = []
        visited: Set[str] = set()

        def _traverse(current_id: str, depth: int):
            if current_id in visited or depth > max_depth:
                return
            visited.add(current_id)

            downstream = self.get_downstream_traceability(current_id)
            for link in downstream:
                result.append({
                    "from_id": link.source_id,
                    "to_id": link.target_id,
                    "link_type": link.link_type.value,
                    "depth": depth,
                    "description": link.description,
                })
                _traverse(link.target_id, depth + 1)

        _traverse(artifact_id, 0)
        return result

    def trace_backward(self, artifact_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Backward traceability analysis - find all upstream items."""
        result = []
        visited: Set[str] = set()

        def _traverse(current_id: str, depth: int):
            if current_id in visited or depth > max_depth:
                return
            visited.add(current_id)

            upstream = self.get_upstream_traceability(current_id)
            for link in upstream:
                result.append({
                    "from_id": link.target_id,
                    "to_id": link.source_id,
                    "link_type": link.link_type.value,
                    "depth": depth,
                    "description": link.description,
                })
                _traverse(link.source_id, depth + 1)

        _traverse(artifact_id, 0)
        return result

    def impact_analysis(self, artifact_id: str) -> Dict[str, Any]:
        """
        Comprehensive impact analysis - what is affected if this artifact changes.
        
        Returns:
            Dict with forward impacts, backward impacts, and affected items
        """
        forward = self.trace_forward(artifact_id)
        backward = self.trace_backward(artifact_id)

        affected_ids: Set[str] = set()
        for item in forward:
            affected_ids.add(item["to_id"])
        for item in backward:
            affected_ids.add(item["from_id"])
        affected_ids.discard(artifact_id)

        # Gather affected requirement details
        affected_requirements = []
        for aid in affected_ids:
            req = self._requirement_manager.get_requirement(aid)
            if req:
                affected_requirements.append(req.to_dict())

        return {
            "artifact_id": artifact_id,
            "forward_impacts": forward,
            "backward_impacts": backward,
            "affected_count": len(affected_ids),
            "affected_requirements": affected_requirements,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def coverage_analysis(self) -> Dict[str, Any]:
        """
        Analyze traceability coverage across requirements.
        
        Returns:
            Coverage report with linked/unlinked requirements, coverage percentage
        """
        all_reqs = self._requirement_manager.get_all_requirements()
        total = len(all_reqs)
        linked_count = 0
        linked_reqs = []
        unlinked_reqs = []

        for req in all_reqs:
            links = self.get_links_for(req.id)
            if links:
                linked_count += 1
                linked_reqs.append({
                    "id": req.id,
                    "title": req.title,
                    "link_count": len(links),
                })
            else:
                unlinked_reqs.append(req.to_dict())

        coverage_pct = (linked_count / total * 100) if total > 0 else 0.0

        return {
            "total_requirements": total,
            "linked_requirements": linked_count,
            "unlinked_requirements": total - linked_count,
            "coverage_percentage": round(coverage_pct, 2),
            "linked_details": linked_reqs,
            "unlinked_details": unlinked_reqs,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def generate_traceability_matrix(self) -> Dict[str, Any]:
        """
        Generate a traceability matrix showing relationships between artifacts.
        
        Returns:
            Matrix representation of traceability relationships
        """
        all_reqs = self._requirement_manager.get_all_requirements()
        req_ids = [r.id for r in all_reqs]

        matrix = {}
        for req in all_reqs:
            row = {"id": req.id, "title": req.title}
            links = self.get_links_for(req.id)
            linked_to = {}
            for link in links:
                other = link.target_id if link.source_id == req.id else link.source_id
                if other in req_ids:
                    linked_to[other] = link.link_type.value
            row["links"] = linked_to
            matrix[req.id] = row

        return {
            "requirements": [r.to_dict() for r in all_reqs],
            "matrix": matrix,
            "total_links": len(self._links),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_all_links(self) -> List[TraceLink]:
        """Get all traceability links."""
        return list(self._links.values())

    def get_links_by_type(self, link_type: TraceLinkType) -> List[TraceLink]:
        """Get links filtered by type."""
        return [l for l in self._links.values() if l.link_type == link_type]

    def get_links_between(self, source_id: str, target_id: str) -> List[TraceLink]:
        """Get links between two specific artifacts."""
        return [
            l for l in self._links.values()
            if (l.source_id == source_id and l.target_id == target_id)
            or (l.source_id == target_id and l.target_id == source_id)
        ]