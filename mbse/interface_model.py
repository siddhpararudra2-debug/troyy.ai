"""
Interface Model - Interface definition and management for MBSE.

Capabilities:
- Interface Modeling
- Interface Definition
- Signal/Data Flow Definition
- Port Type Management
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime


class InterfaceType(str):
    """Types of interfaces."""
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    DATA = "data"
    FLUID = "fluid"
    OPTICAL = "optical"
    THERMAL = "thermal"
    RF = "radio_frequency"
    SOFTWARE = "software"


class InterfaceDefinition:
    """Definition of an interface between system elements."""

    def __init__(
        self,
        iface_id: str,
        name: str,
        iface_type: InterfaceType,
        description: Optional[str] = None,
    ):
        self.id = iface_id
        self.name = name
        self.interface_type = iface_type
        self.description = description
        self.signals: List[Dict[str, Any]] = []
        self.parameters: Dict[str, Any] = {}
        self.protocols: List[str] = []
        self.constraints: List[str] = []

    def add_signal(self, name: str, signal_type: str, direction: str, description: Optional[str] = None):
        """Add a signal/data element to this interface."""
        self.signals.append({
            "name": name,
            "type": signal_type,
            "direction": direction,
            "description": description,
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "interface_type": self.interface_type,
            "description": self.description,
            "signals": self.signals,
            "parameters": self.parameters,
            "protocols": self.protocols,
            "constraints": self.constraints,
        }


class InterfaceModel:
    """
    Manages interface definitions between system elements.
    Supports multiple interface types and signal definitions.
    """

    def __init__(self):
        self._interfaces: Dict[str, InterfaceDefinition] = {}
        self._port_mappings: Dict[str, Dict[str, str]] = {}  # port_id -> {interface_id}

    def create_interface(
        self,
        name: str,
        iface_type: InterfaceType = InterfaceType.DATA,
        description: Optional[str] = None,
    ) -> InterfaceDefinition:
        """Create a new interface definition."""
        iface_id = str(uuid.uuid4())
        iface = InterfaceDefinition(
            iface_id=iface_id,
            name=name,
            iface_type=iface_type,
            description=description,
        )
        self._interfaces[iface_id] = iface
        return iface

    def map_port_to_interface(self, port_id: str, interface_id: str) -> bool:
        """Map a port to an interface."""
        if interface_id not in self._interfaces:
            return False
        if port_id not in self._port_mappings:
            self._port_mappings[port_id] = {}
        self._port_mappings[port_id][interface_id] = interface_id
        return True

    def get_interfaces_for_port(self, port_id: str) -> List[InterfaceDefinition]:
        """Get interfaces mapped to a port."""
        if port_id not in self._port_mappings:
            return []
        return [
            self._interfaces[iface_id]
            for iface_id in self._port_mappings[port_id]
            if iface_id in self._interfaces
        ]

    def get_interface(self, interface_id: str) -> Optional[InterfaceDefinition]:
        """Get interface by ID."""
        return self._interfaces.get(interface_id)

    def get_all_interfaces(self) -> List[InterfaceDefinition]:
        """Get all interfaces."""
        return list(self._interfaces.values())

    def generate_interface_control_document(self) -> Dict[str, Any]:
        """Generate an Interface Control Document (ICD)."""
        return {
            "interfaces": [iface.to_dict() for iface in self._interfaces.values()],
            "port_mappings": self._port_mappings,
            "generated_at": datetime.utcnow().isoformat(),
        }