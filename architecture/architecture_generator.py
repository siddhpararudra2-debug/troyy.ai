"""
Architecture Generator - Generates system architectures from requirements.

Capabilities:
- System Breakdown
- Architecture Tree Generation
- Interface Maps
- Subsystem Design
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime


class ArchitectureTree:
    """A hierarchical architecture tree."""

    def __init__(self, name: str, description: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.root_id: Optional[str] = None
        self._nodes: Dict[str, Dict[str, Any]] = {}

    def add_node(self, name: str, node_type: str, parent_id: Optional[str] = None,
                 description: Optional[str] = None, properties: Optional[Dict] = None) -> str:
        node_id = str(uuid.uuid4())
        self._nodes[node_id] = {
            "id": node_id,
            "name": name,
            "type": node_type,
            "parent_id": parent_id,
            "description": description,
            "properties": properties or {},
            "children": [],
        }
        if parent_id and parent_id in self._nodes:
            self._nodes[parent_id]["children"].append(node_id)
        if parent_id is None:
            self.root_id = node_id
        return node_id

    def to_dict(self) -> Dict[str, Any]:
        def _build(node_id: str) -> Dict[str, Any]:
            node = self._nodes[node_id]
            return {
                **node,
                "children": [_build(cid) for cid in node["children"] if cid in self._nodes],
            }
        if not self.root_id:
            return {"name": self.name, "children": []}
        return _build(self.root_id)


class ArchitectureGenerator:
    """
    Generates system architectures by breaking down systems
    into subsystems, components, and interfaces.
    """

    def __init__(self):
        self._architectures: Dict[str, ArchitectureTree] = {}
        self._interface_maps: Dict[str, List[Dict[str, Any]]] = {}

    def generate_from_requirements(
        self,
        system_name: str,
        requirements: List[Dict[str, Any]],
    ) -> ArchitectureTree:
        """Generate architecture tree from requirements."""
        tree = ArchitectureTree(system_name)
        root_id = tree.add_node(system_name, "system", description=f"System: {system_name}")

        # Group requirements by type for subsystem identification
        subsystems = self._identify_subsystems(requirements)

        for sub_name, sub_reqs in subsystems.items():
            sub_id = tree.add_node(
                sub_name, "subsystem",
                parent_id=root_id,
                description=f"Subsystem: {sub_name}",
                properties={"requirement_count": len(sub_reqs)},
            )

            for req in sub_reqs:
                tree.add_node(
                    req.get("title", "Requirement"),
                    "requirement",
                    parent_id=sub_id,
                    description=req.get("description"),
                )

        self._architectures[tree.id] = tree
        return tree

    def _identify_subsystems(self, requirements: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Identify subsystem groupings from requirements."""
        subsystems: Dict[str, List[Dict]] = {}
        keywords_map = {
            "Flight Controller": ["flight", "control", "navigation", "guidance", "autopilot"],
            "Power System": ["power", "energy", "battery", "voltage", "current", "power supply"],
            "Payload": ["payload", "sensor", "camera", "instrument", "mission equipment"],
            "Communication": ["communication", "telemetry", "radio", "antenna", "data link", "transceiver"],
            "Propulsion": ["propulsion", "motor", "thruster", "engine", "propeller", "thrust"],
            "Structure": ["structure", "frame", "housing", "chassis", "mount", "enclosure"],
            "Thermal": ["thermal", "temperature", "cooling", "heat", "heater"],
            "Avionics": ["avionics", "processor", "computer", "electronics", "sensor suite"],
        }

        for req in requirements:
            desc = (req.get("title", "") + " " + req.get("description", "")).lower()
            assigned = False
            for subsystem, keywords in keywords_map.items():
                if any(kw in desc for kw in keywords):
                    if subsystem not in subsystems:
                        subsystems[subsystem] = []
                    subsystems[subsystem].append(req)
                    assigned = True
                    break
            if not assigned:
                if "Other" not in subsystems:
                    subsystems["Other"] = []
                subsystems["Other"].append(req)

        return subsystems

    def generate_interface_map(self, tree_id: str) -> List[Dict[str, Any]]:
        """Generate interface map between subsystems."""
        tree = self._architectures.get(tree_id)
        if not tree:
            return []

        interfaces = []
        nodes = list(tree._nodes.values())
        subsystems = [n for n in nodes if n["type"] == "subsystem"]

        for i, sub_a in enumerate(subsystems):
            for sub_b in subsystems[i + 1:]:
                interface = {
                    "id": str(uuid.uuid4()),
                    "source": sub_a["name"],
                    "target": sub_b["name"],
                    "type": "data" if "Communication" in [sub_a["name"], sub_b["name"]] else "physical",
                    "description": f"Interface between {sub_a['name']} and {sub_b['name']}",
                }
                interfaces.append(interface)

        self._interface_maps[tree_id] = interfaces
        return interfaces

    def build_drone_architecture(self) -> ArchitectureTree:
        """Build a standard drone architecture as an example."""
        tree = ArchitectureTree("Drone System")
        root = tree.add_node("Drone", "system", description="Unmanned Aerial Vehicle")

        fc = tree.add_node("Flight Controller", "subsystem", parent_id=root,
                           description="Main flight control and navigation")
        tree.add_node("IMU", "component", parent_id=fc, description="Inertial Measurement Unit")
        tree.add_node("GPS", "component", parent_id=fc, description="Global Positioning System")
        tree.add_node("Autopilot", "component", parent_id=fc, description="Autonomous flight control")

        power = tree.add_node("Power System", "subsystem", parent_id=root,
                              description="Power generation and distribution")
        tree.add_node("Battery", "component", parent_id=power, description="Lithium Polymer Battery")
        tree.add_node("Power Distribution", "component", parent_id=power, description="Power management board")
        tree.add_node("BEC", "component", parent_id=power, description="Battery Eliminator Circuit")

        payload = tree.add_node("Payload", "subsystem", parent_id=root,
                                description="Mission payload equipment")
        tree.add_node("Camera", "component", parent_id=payload, description="Optical camera system")
        tree.add_node("Gimbal", "component", parent_id=payload, description="Camera stabilization")

        comm = tree.add_node("Communication", "subsystem", parent_id=root,
                             description="Data link and telemetry")
        tree.add_node("Radio Link", "component", parent_id=comm, description="RC control link")
        tree.add_node("Telemetry", "component", parent_id=comm, description="Data telemetry module")

        prop = tree.add_node("Propulsion", "subsystem", parent_id=root,
                             description="Propulsion system")
        tree.add_node("Motor", "component", parent_id=prop, description="Brushless DC motor")
        tree.add_node("ESC", "component", parent_id=prop, description="Electronic Speed Controller")
        tree.add_node("Propeller", "component", parent_id=prop, description="Propeller blades")

        self._architectures[tree.id] = tree
        return tree

    def get_architecture(self, tree_id: str) -> Optional[ArchitectureTree]:
        return self._architectures.get(tree_id)