"""
System Model - MBSE system modeling with SysML concepts.

Capabilities:
- System Modeling
- Functional Decomposition
- SysML Concept Support
- Requirement Links
"""

import uuid
from enum import Enum
from typing import Optional, List, Dict, Any, Set
from datetime import datetime


class ModelElementType(str, Enum):
    """SysML-compatible model element types."""
    SYSTEM = "system"
    SUBSYSTEM = "subsystem"
    COMPONENT = "component"
    PART = "part"
    PORT = "port"
    INTERFACE = "interface"
    CONNECTOR = "connector"
    CONSTRAINT = "constraint"
    VALUE_TYPE = "value_type"
    UNIT = "unit"
    BLOCK = "block"
    ACTOR = "actor"
    USE_CASE = "use_case"
    ACTIVITY = "activity"
    STATE = "state"
    REQUIREMENT = "requirement"


class ModelRelationType(str, Enum):
    """Types of relationships between model elements."""
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"
    ASSOCIATION = "association"
    GENERALIZATION = "generalization"
    REALIZATION = "realization"
    DEPENDENCY = "dependency"
    FLOW = "flow"
    ALLOCATION = "allocation"


class ModelProperty:
    """A property/attribute of a model element."""

    def __init__(
        self,
        name: str,
        value_type: str,
        value: Any = None,
        units: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.value_type = value_type
        self.value = value
        self.units = units
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value_type": self.value_type,
            "value": self.value,
            "units": self.units,
            "description": self.description,
        }


class ModelElement:
    """Base model element for MBSE."""

    def __init__(
        self,
        element_id: str,
        name: str,
        element_type: ModelElementType,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        properties: Optional[Dict[str, ModelProperty]] = None,
    ):
        self.id = element_id
        self.name = name
        self.element_type = element_type
        self.description = description
        self.parent_id = parent_id
        self.properties = properties or {}
        self.child_ids: List[str] = []
        self.port_ids: List[str] = []
        self.constraint_ids: List[str] = []
        self.requirement_ids: List[str] = []
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.version = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "element_type": self.element_type.value,
            "description": self.description,
            "parent_id": self.parent_id,
            "child_ids": self.child_ids,
            "port_ids": self.port_ids,
            "constraint_ids": self.constraint_ids,
            "requirement_ids": self.requirement_ids,
            "properties": {k: v.to_dict() for k, v in self.properties.items()},
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }


class ModelRelation:
    """Relationship between model elements."""

    def __init__(
        self,
        relation_id: str,
        source_id: str,
        target_id: str,
        relation_type: ModelRelationType,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.id = relation_id
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.name = name
        self.description = description
        self.properties: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value,
            "name": self.name,
            "description": self.description,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
        }


class Port:
    """Interface port on a model element."""

    def __init__(
        self,
        port_id: str,
        name: str,
        direction: str = "bidirectional",
        description: Optional[str] = None,
    ):
        self.id = port_id
        self.name = name
        self.direction = direction  # input, output, bidirectional
        self.description = description
        self.interface_type: Optional[str] = None
        self.connected_port_ids: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "direction": self.direction,
            "description": self.description,
            "interface_type": self.interface_type,
            "connected_port_ids": self.connected_port_ids,
        }


class SystemModel:
    """
    MBSE System Model - manages the complete system model with
    hierarchical decomposition, interfaces, and relationships.
    """

    def __init__(self, name: str = "System Model", description: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self._elements: Dict[str, ModelElement] = {}
        self._relations: Dict[str, ModelRelation] = {}
        self._ports: Dict[str, Port] = {}

    def create_element(
        self,
        name: str,
        element_type: ModelElementType,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> ModelElement:
        """Create a new model element."""
        element_id = str(uuid.uuid4())
        element = ModelElement(
            element_id=element_id,
            name=name,
            element_type=element_type,
            description=description,
            parent_id=parent_id,
        )
        self._elements[element_id] = element

        if parent_id and parent_id in self._elements:
            self._elements[parent_id].child_ids.append(element_id)

        return element

    def get_element(self, element_id: str) -> Optional[ModelElement]:
        """Get element by ID."""
        return self._elements.get(element_id)

    def update_element(self, element_id: str, **kwargs) -> Optional[ModelElement]:
        """Update element properties."""
        element = self._elements.get(element_id)
        if element:
            for key, value in kwargs.items():
                if hasattr(element, key):
                    setattr(element, key, value)
            element.updated_at = datetime.utcnow()
            element.version += 1
        return element

    def delete_element(self, element_id: str) -> bool:
        """Remove an element."""
        if element_id in self._elements:
            # Remove from parent
            element = self._elements[element_id]
            if element.parent_id and element.parent_id in self._elements:
                parent = self._elements[element.parent_id]
                if element_id in parent.child_ids:
                    parent.child_ids.remove(element_id)
            # Remove relations
            to_delete = [
                rid for rid, rel in self._relations.items()
                if rel.source_id == element_id or rel.target_id == element_id
            ]
            for rid in to_delete:
                del self._relations[rid]
            del self._elements[element_id]
            return True
        return False

    def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: ModelRelationType,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[ModelRelation]:
        """Create a relation between two elements."""
        if source_id not in self._elements or target_id not in self._elements:
            return None
        relation_id = str(uuid.uuid4())
        relation = ModelRelation(
            relation_id=relation_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            name=name,
            description=description,
        )
        self._relations[relation_id] = relation
        return relation

    def create_port(
        self,
        element_id: str,
        name: str,
        direction: str = "bidirectional",
        description: Optional[str] = None,
    ) -> Optional[Port]:
        """Create a port on an element."""
        if element_id not in self._elements:
            return None
        port_id = str(uuid.uuid4())
        port = Port(
            port_id=port_id,
            name=name,
            direction=direction,
            description=description,
        )
        self._ports[port_id] = port
        self._elements[element_id].port_ids.append(port_id)
        return port

    def connect_ports(self, port_a_id: str, port_b_id: str) -> bool:
        """Connect two ports."""
        if port_a_id not in self._ports or port_b_id not in self._ports:
            return False
        self._ports[port_a_id].connected_port_ids.append(port_b_id)
        self._ports[port_b_id].connected_port_ids.append(port_a_id)
        return True

    def get_element_tree(self, root_id: Optional[str] = None) -> Dict[str, Any]:
        """Get hierarchical element tree."""
        if root_id and root_id in self._elements:
            roots = [self._elements[root_id]]
        else:
            roots = [e for e in self._elements.values() if e.parent_id is None]

        def _build_tree(element: ModelElement) -> Dict[str, Any]:
            children = []
            for child_id in element.child_ids:
                if child_id in self._elements:
                    children.append(_build_tree(self._elements[child_id]))
            return {
                "element": element.to_dict(),
                "children": children,
            }

        return {
            "model": {"id": self.id, "name": self.name},
            "trees": [_build_tree(r) for r in roots],
        }

    def get_relations_for(self, element_id: str) -> List[ModelRelation]:
        """Get all relations for an element."""
        return [
            r for r in self._relations.values()
            if r.source_id == element_id or r.target_id == element_id
        ]

    def get_elements_by_type(self, element_type: ModelElementType) -> List[ModelElement]:
        """Get all elements of a specific type."""
        return [e for e in self._elements.values() if e.element_type == element_type]

    def link_requirement(self, element_id: str, requirement_id: str) -> bool:
        """Link a requirement to an element."""
        if element_id in self._elements:
            if requirement_id not in self._elements[element_id].requirement_ids:
                self._elements[element_id].requirement_ids.append(requirement_id)
            return True
        return False

    def get_all_elements(self) -> List[ModelElement]:
        """Get all elements."""
        return list(self._elements.values())

    def get_all_relations(self) -> List[ModelRelation]:
        """Get all relations."""
        return list(self._relations.values())

    def export_model(self) -> Dict[str, Any]:
        """Export the complete system model."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "elements": [e.to_dict() for e in self._elements.values()],
            "relations": [r.to_dict() for r in self._relations.values()],
            "ports": [p.to_dict() for p in self._ports.values()],
        }