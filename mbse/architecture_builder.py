"""
Architecture Builder - System architecture modeling and construction.

Capabilities:
- Architecture Modeling
- System Decomposition
- Architecture Views
- SysML Block Definition Diagrams
"""

import uuid
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from mbse.system_model import (
    SystemModel, ModelElement, ModelElementType,
    ModelRelationType, ModelRelation, Port,
)


class ArchitectureView:
    """A specific view of the system architecture."""

    def __init__(
        self,
        view_id: str,
        name: str,
        view_type: str,
        description: Optional[str] = None,
    ):
        self.id = view_id
        self.name = name
        self.view_type = view_type  # structural, behavioral, functional, interface
        self.description = description
        self.element_ids: List[str] = []
        self.relation_ids: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "view_type": self.view_type,
            "description": self.description,
            "element_ids": self.element_ids,
            "relation_ids": self.relation_ids,
        }


class ArchitectureBuilder:
    """
    Builds system architectures with hierarchical decomposition.
    Supports multiple architecture views and SysML concepts.
    """

    def __init__(self, system_model: Optional[SystemModel] = None):
        self._model = system_model or SystemModel()
        self._views: Dict[str, ArchitectureView] = {}

    @property
    def model(self) -> SystemModel:
        return self._model

    def create_view(
        self,
        name: str,
        view_type: str,
        description: Optional[str] = None,
    ) -> ArchitectureView:
        """Create an architecture view."""
        view_id = str(uuid.uuid4())
        view = ArchitectureView(
            view_id=view_id,
            name=name,
            view_type=view_type,
            description=description,
        )
        self._views[view_id] = view
        return view

    def add_element_to_view(self, view_id: str, element_id: str) -> bool:
        """Add an element to a view."""
        if view_id in self._views and self._model.get_element(element_id):
            if element_id not in self._views[view_id].element_ids:
                self._views[view_id].element_ids.append(element_id)
            return True
        return False

    def build_system_architecture(
        self,
        system_name: str,
        subsystems: List[Dict[str, Any]],
        interfaces: List[Dict[str, Any]],
    ) -> SystemModel:
        """
        Build a complete system architecture from a structured description.
        
        Args:
            system_name: Name of the system
            subsystems: List of subsystem definitions with name, description, components
            interfaces: List of interface definitions between subsystems
        """
        # Create root system
        root = self._model.create_element(
            name=system_name,
            element_type=ModelElementType.SYSTEM,
            description=f"Top-level system: {system_name}",
        )

        # Create subsystems and components
        for sub_def in subsystems:
            subsystem = self._model.create_element(
                name=sub_def["name"],
                element_type=ModelElementType.SUBSYSTEM,
                description=sub_def.get("description"),
                parent_id=root.id,
            )

            for comp_def in sub_def.get("components", []):
                component = self._model.create_element(
                    name=comp_def["name"],
                    element_type=ModelElementType.COMPONENT,
                    description=comp_def.get("description"),
                    parent_id=subsystem.id,
                )

                # Create ports on components
                for port_def in comp_def.get("ports", []):
                    self._model.create_port(
                        element_id=component.id,
                        name=port_def["name"],
                        direction=port_def.get("direction", "bidirectional"),
                        description=port_def.get("description"),
                    )

        # Create interfaces between subsystems/components
        for iface_def in interfaces:
            source = self._find_element_by_name(iface_def["source"])
            target = self._find_element_by_name(iface_def["target"])
            if source and target:
                self._model.create_relation(
                    source_id=source.id,
                    target_id=target.id,
                    relation_type=ModelRelationType.ASSOCIATION,
                    name=iface_def.get("name", f"{source.name}-{target.name}"),
                    description=iface_def.get("description"),
                )

        return self._model

    def _find_element_by_name(self, name: str) -> Optional[ModelElement]:
        """Find an element by name."""
        for element in self._model.get_all_elements():
            if element.name == name:
                return element
        return None

    def generate_block_definition_diagram(self) -> Dict[str, Any]:
        """Generate a SysML Block Definition Diagram representation."""
        elements = self._model.get_all_elements()
        relations = self._model.get_all_relations()

        blocks = []
        for element in elements:
            block = {
                "id": element.id,
                "name": element.name,
                "type": element.element_type.value,
                "parent": element.parent_id,
                "properties": [
                    {
                        "name": k,
                        "type": v.value_type,
                        "value": v.value,
                    }
                    for k, v in element.properties.items()
                ],
                "ports": [
                    p.to_dict() for p_id, p in
                    [(pid, self._model._ports.get(pid)) for pid in element.port_ids]
                    if p is not None
                ],
            }
            blocks.append(block)

        connectors = []
        for rel in relations:
            connector = {
                "id": rel.id,
                "name": rel.name,
                "source": rel.source_id,
                "target": rel.target_id,
                "type": rel.relation_type.value,
            }
            connectors.append(connector)

        return {
            "type": "BlockDefinitionDiagram",
            "name": self._model.name,
            "blocks": blocks,
            "connectors": connectors,
        }

    def generate_internal_block_diagram(self) -> Dict[str, Any]:
        """Generate an Internal Block Diagram showing internal structure."""
        elements = self._model.get_all_elements()
        relations = self._model.get_all_relations()

        parts = []
        for element in elements:
            if element.parent_id is not None:
                parts.append({
                    "id": element.id,
                    "name": element.name,
                    "type": element.element_type.value,
                    "part_of": element.parent_id,
                })

        flows = []
        for rel in relations:
            flow = {
                "id": rel.id,
                "name": rel.name,
                "from": rel.source_id,
                "to": rel.target_id,
                "type": rel.relation_type.value,
            }
            flows.append(flow)

        return {
            "type": "InternalBlockDiagram",
            "name": self._model.name,
            "parts": parts,
            "flows": flows,
        }

    def analyze_architecture(self) -> Dict[str, Any]:
        """Analyze architecture for completeness and issues."""
        elements = self._model.get_all_elements()
        relations = self._model.get_all_relations()

        # Count by type
        type_counts: Dict[str, int] = {}
        for e in elements:
            type_counts[e.element_type.value] = type_counts.get(e.element_type.value, 0) + 1

        # Find unconnected elements
        element_ids = {e.id for e in elements}
        connected_ids: set = set()
        for r in relations:
            connected_ids.add(r.source_id)
            connected_ids.add(r.target_id)
        unconnected = element_ids - connected_ids - {e.id for e in elements if not e.child_ids}

        # Find elements without ports
        no_ports = [e for e in elements if not e.port_ids and e.element_type == ModelElementType.COMPONENT]

        return {
            "total_elements": len(elements),
            "total_relations": len(relations),
            "by_type": type_counts,
            "unconnected_elements": [
                {"id": e.id, "name": e.name} for e in elements if e.id in unconnected
            ],
            "components_without_ports": [
                {"id": e.id, "name": e.name} for e in no_ports
            ],
            "has_interfaces": len([r for r in relations if r.relation_type == ModelRelationType.ASSOCIATION]) > 0,
        }

    def get_all_views(self) -> List[ArchitectureView]:
        """Get all architecture views."""
        return list(self._views.values())