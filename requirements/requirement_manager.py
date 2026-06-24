"""
Requirement Manager - Requirements Management Engine for Sprint 6.

Capabilities:
- Requirement Capture
- Requirement Classification
- Requirement Tree Management
- Functional / Performance / Safety / Manufacturing / Mission Requirements
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any, Set
from datetime import datetime


class RequirementType(str, Enum):
    """Types of engineering requirements."""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    MANUFACTURING = "manufacturing"
    MISSION = "mission"
    INTERFACE = "interface"
    RELIABILITY = "reliability"
    MAINTAINABILITY = "maintainability"
    ENVIRONMENTAL = "environmental"
    REGULATORY = "regulatory"


class RequirementPriority(str, Enum):
    """Requirement priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(str, Enum):
    """Requirement status in the lifecycle."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    VERIFIED = "verified"
    VALIDATED = "validated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


class Requirement:
    """Individual engineering requirement."""

    def __init__(
        self,
        req_id: str,
        title: str,
        description: str,
        req_type: RequirementType = RequirementType.FUNCTIONAL,
        priority: RequirementPriority = RequirementPriority.MEDIUM,
        status: RequirementStatus = RequirementStatus.DRAFT,
        source: Optional[str] = None,
        owner: Optional[str] = None,
        verification_method: Optional[str] = None,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = req_id
        self.title = title
        self.description = description
        self.req_type = req_type
        self.priority = priority
        self.status = status
        self.source = source
        self.owner = owner
        self.verification_method = verification_method
        self.parent_id = parent_id
        self.metadata = metadata or {}
        self.child_ids: List[str] = []
        self.traceability_links: List[str] = []
        self.risk_ids: List[str] = []
        self.revision_history: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        """Serialize requirement to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "req_type": self.req_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "source": self.source,
            "owner": self.owner,
            "verification_method": self.verification_method,
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "traceability_links": self.traceability_links,
            "risk_ids": self.risk_ids,
            "revision_history": self.revision_history,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "metadata": self.metadata,
        }

    def update(self, **kwargs):
        """Update requirement attributes with revision tracking."""
        revision = {
            "timestamp": datetime.utcnow().isoformat(),
            "previous_state": {
                "title": self.title,
                "description": self.description,
                "status": self.status.value,
                "priority": self.priority.value,
            },
            "changes": kwargs,
        }
        self.revision_history.append(revision)
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        self.version += 1


class RequirementNode:
    """Tree node for requirement hierarchy."""

    def __init__(self, requirement: Requirement):
        self.requirement = requirement
        self.children: List["RequirementNode"] = []
        self.parent: Optional["RequirementNode"] = None

    def add_child(self, child: "RequirementNode"):
        child.parent = self
        self.children.append(child)
        if child.requirement.id not in self.requirement.child_ids:
            self.requirement.child_ids.append(child.requirement.id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement": self.requirement.to_dict(),
            "children": [c.to_dict() for c in self.children],
        }


class RequirementManager:
    """
    Central requirements management engine.
    Manages the full lifecycle of engineering requirements.
    """

    def __init__(self):
        self._requirements: Dict[str, Requirement] = {}
        self._trees: List[RequirementNode] = []

    def create_requirement(
        self,
        title: str,
        description: str,
        req_type: RequirementType = RequirementType.FUNCTIONAL,
        priority: RequirementPriority = RequirementPriority.MEDIUM,
        source: Optional[str] = None,
        owner: Optional[str] = None,
        verification_method: Optional[str] = None,
        parent_id: Optional[str] = None,
        **kwargs,
    ) -> Requirement:
        """Create a new requirement."""
        req_id = str(uuid.uuid4())
        req = Requirement(
            req_id=req_id,
            title=title,
            description=description,
            req_type=req_type,
            priority=priority,
            source=source,
            owner=owner,
            verification_method=verification_method,
            parent_id=parent_id,
            metadata=kwargs,
        )
        self._requirements[req_id] = req

        if parent_id and parent_id in self._requirements:
            self._requirements[parent_id].child_ids.append(req_id)

        return req

    def get_requirement(self, req_id: str) -> Optional[Requirement]:
        """Get requirement by ID."""
        return self._requirements.get(req_id)

    def update_requirement(self, req_id: str, **kwargs) -> Optional[Requirement]:
        """Update an existing requirement."""
        req = self._requirements.get(req_id)
        if req:
            req.update(**kwargs)
        return req

    def delete_requirement(self, req_id: str) -> bool:
        """Soft delete a requirement."""
        req = self._requirements.get(req_id)
        if req:
            req.status = RequirementStatus.SUPERSEDED
            return True
        return False

    def get_requirements_by_type(self, req_type: RequirementType) -> List[Requirement]:
        """Get all requirements of a given type."""
        return [r for r in self._requirements.values() if r.req_type == req_type]

    def get_requirements_by_status(self, status: RequirementStatus) -> List[Requirement]:
        """Get all requirements with given status."""
        return [r for r in self._requirements.values() if r.status == status]

    def build_tree(self, root_requirement_ids: Optional[List[str]] = None) -> List[RequirementNode]:
        """Build a requirement tree from root requirements."""
        if root_requirement_ids:
            roots = [self._requirements[rid] for rid in root_requirement_ids if rid in self._requirements]
        else:
            roots = [r for r in self._requirements.values() if r.parent_id is None]

        trees = []
        for root_req in roots:
            node = self._build_node(root_req)
            trees.append(node)

        self._trees = trees
        return trees

    def _build_node(self, requirement: Requirement) -> RequirementNode:
        """Recursively build a requirement tree node."""
        node = RequirementNode(requirement)
        for child_id in requirement.child_ids:
            if child_id in self._requirements:
                child_node = self._build_node(self._requirements[child_id])
                node.add_child(child_node)
        return node

    def add_traceability_link(self, from_req_id: str, to_req_id: str) -> bool:
        """Add a traceability link between requirements."""
        if from_req_id in self._requirements and to_req_id in self._requirements:
            if to_req_id not in self._requirements[from_req_id].traceability_links:
                self._requirements[from_req_id].traceability_links.append(to_req_id)
            if from_req_id not in self._requirements[to_req_id].traceability_links:
                self._requirements[to_req_id].traceability_links.append(from_req_id)
            return True
        return False

    def get_traceability_chain(self, req_id: str) -> List[Requirement]:
        """Get the full traceability chain for a requirement."""
        chain = []
        visited: Set[str] = set()

        def _traverse(current_id: str):
            if current_id in visited or current_id not in self._requirements:
                return
            visited.add(current_id)
            req = self._requirements[current_id]
            chain.append(req)
            for linked_id in req.traceability_links:
                _traverse(linked_id)

        _traverse(req_id)
        return chain

    def search_requirements(self, query: str) -> List[Requirement]:
        """Search requirements by title or description."""
        query_lower = query.lower()
        return [
            r for r in self._requirements.values()
            if query_lower in r.title.lower() or query_lower in r.description.lower()
        ]

    def get_all_requirements(self) -> List[Requirement]:
        """Get all requirements."""
        return list(self._requirements.values())

    def count_by_type(self) -> Dict[str, int]:
        """Count requirements by type."""
        counts: Dict[str, int] = {}
        for r in self._requirements.values():
            counts[r.req_type.value] = counts.get(r.req_type.value, 0) + 1
        return counts

    def generate_tree_report(self) -> Dict[str, Any]:
        """Generate a comprehensive requirement tree report."""
        trees = self.build_tree()
        return {
            "total_requirements": len(self._requirements),
            "by_type": self.count_by_type(),
            "trees": [t.to_dict() for t in trees],
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_unlinked_requirements(self) -> List[Requirement]:
        """Get requirements with no traceability links."""
        return [r for r in self._requirements.values() if not r.traceability_links]