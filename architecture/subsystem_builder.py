"""
Subsystem Builder - Designs and configures subsystems within the architecture.

Capabilities:
- Subsystem Design
- Component Selection
- Subsystem Interface Definition
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime


class Subsystem:
    """A subsystem within the overall system architecture."""

    def __init__(
        self,
        sub_id: str,
        name: str,
        subsystem_type: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ):
        self.id = sub_id
        self.name = name
        self.subsystem_type = subsystem_type
        self.description = description
        self.parent_id = parent_id
        self.components: List[Dict[str, Any]] = []
        self.interfaces: List[str] = []
        self.requirements: List[str] = []
        self.parameters: Dict[str, Any] = {}
        self.constraints: List[str] = []

    def add_component(self, name: str, component_type: str, quantity: int = 1,
                      description: Optional[str] = None, specifications: Optional[Dict] = None):
        comp = {
            "id": str(uuid.uuid4()),
            "name": name,
            "type": component_type,
            "quantity": quantity,
            "description": description,
            "specifications": specifications or {},
        }
        self.components.append(comp)
        return comp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "subsystem_type": self.subsystem_type,
            "description": self.description,
            "parent_id": self.parent_id,
            "components": self.components,
            "interfaces": self.interfaces,
            "requirements": self.requirements,
            "parameters": self.parameters,
            "constraints": self.constraints,
        }


class SubsystemBuilder:
    """Builds and configures subsystems for the system architecture."""

    def __init__(self):
        self._subsystems: Dict[str, Subsystem] = {}

    def create_subsystem(
        self,
        name: str,
        subsystem_type: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> Subsystem:
        sub_id = str(uuid.uuid4())
        subsystem = Subsystem(
            sub_id=sub_id,
            name=name,
            subsystem_type=subsystem_type,
            description=description,
            parent_id=parent_id,
        )
        self._subsystems[sub_id] = subsystem
        return subsystem

    def get_subsystem(self, sub_id: str) -> Optional[Subsystem]:
        return self._subsystems.get(sub_id)

    def get_all_subsystems(self) -> List[Subsystem]:
        return list(self._subsystems.values())


class ComponentSelector:
    """Selects and configures components for subsystems."""

    @staticmethod
    def select_flight_controller(requirements: Dict[str, Any]) -> Dict[str, Any]:
        recs = []
        if requirements.get("autonomous", False):
            recs.append({"name": "Pixhawk Cube Orange+", "processor": "STM32H7", "features": ["autopilot", "RTK GPS"]})
        recs.append({"name": "Pixhawk 4", "processor": "STM32F765", "features": ["PX4", "ArduPilot"]})
        recs.append({"name": "Navio2", "processor": "Raspberry Pi", "features": ["Linux-based"]})
        return {"recommendations": recs, "count": len(recs)}

    @staticmethod
    def select_battery(requirements: Dict[str, Any]) -> Dict[str, Any]:
        voltage = requirements.get("voltage", 22.2)
        capacity = requirements.get("capacity", 5000)
        recs = [
            {"name": f"LiPo {voltage}V {capacity}mAh", "type": "LiPo", "cells": int(voltage / 3.7)},
            {"name": f"Li-Ion {voltage}V {capacity}mAh", "type": "Li-Ion", "cells": int(voltage / 3.6)},
        ]
        return {"recommendations": recs, "voltage": voltage, "capacity": capacity}