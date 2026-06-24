"""Formation Controller - Module 2 for Sprint 13."""
from typing import List, Dict, Any, Tuple


class FormationController:
    def __init__(self):
        self.formations = {
            "line": self._line_formation,
            "column": self._column_formation,
            "wedge": self._wedge_formation,
            "diamond": self._diamond_formation,
        }

    def establish_formation(
        self,
        swarm_id: str,
        formation_type: str,
        leader_position: Dict[str, float],
        agents_count: int = 4
    ) -> Tuple[bool, Dict[str, Any]]:
        if formation_type not in self.formations:
            return False, {"error": "Formation not supported"}
        
        positions = self.formations[formation_type](leader_position, agents_count)
        return True, {
            "swarm_id": swarm_id,
            "formation_type": formation_type,
            "positions": positions,
        }

    def _line_formation(self, leader: Dict[str, float], count: int) -> List[Dict[str, float]]:
        positions = []
        spacing = 5.0
        for i in range(1, count):
            positions.append({
                "x": leader["x"],
                "y": leader["y"] + (i * spacing),
                "z": leader["z"],
            })
        return positions

    def _column_formation(self, leader: Dict[str, float], count: int) -> List[Dict[str, float]]:
        positions = []
        spacing = 5.0
        for i in range(1, count):
            positions.append({
                "x": leader["x"] + (i * spacing),
                "y": leader["y"],
                "z": leader["z"],
            })
        return positions

    def _wedge_formation(self, leader: Dict[str, float], count: int) -> List[Dict[str, float]]:
        positions = []
        spacing = 5.0
        for i in range(1, count):
            side = 1 if i % 2 == 1 else -1
            row = (i + 1) // 2
            positions.append({
                "x": leader["x"] + (row * spacing),
                "y": leader["y"] + (side * row * spacing * 0.5),
                "z": leader["z"],
            })
        return positions

    def _diamond_formation(self, leader: Dict[str, float], count: int) -> List[Dict[str, float]]:
        positions = []
        spacing = 5.0
        if count > 1:
            positions.append({"x": leader["x"] + spacing, "y": leader["y"], "z": leader["z"]})
        if count > 2:
            positions.append({"x": leader["x"], "y": leader["y"] + spacing, "z": leader["z"]})
        if count > 3:
            positions.append({"x": leader["x"], "y": leader["y"] - spacing, "z": leader["z"]})
        return positions

    def move_formation(
        self,
        swarm_id: str,
        target_position: Dict[str, float],
        heading: float = 0.0,
        speed: float = 10.0
    ) -> Tuple[bool, Dict[str, Any]]:
        return True, {
            "swarm_id": swarm_id,
            "target": target_position,
            "heading": heading,
            "speed": speed,
        }
