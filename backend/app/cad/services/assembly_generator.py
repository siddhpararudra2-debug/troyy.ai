"""
Assembly Generator - Creates multi-part assemblies
"""
from typing import Dict, Any, List, Optional, Tuple
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AssemblyGenerator:
    """Generates and manages CAD assemblies."""
    
    def __init__(self):
        self.mating_engine = MatingEngine()
        self.interference_checker = InterferenceChecker()
    
    def create_assembly(
        self, 
        name: str, 
        project_id: str,
        parts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Create a new assembly."""
        assembly = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "name": name,
            "parts": parts or [],
            "mates": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        return assembly
    
    def add_part(
        self, 
        assembly: Dict[str, Any], 
        part: Dict[str, Any],
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """Add a part to assembly."""
        assembly_part = {
            "part_id": part["id"],
            "part": part,
            "position": position or [0, 0, 0],
            "rotation": rotation or [0, 0, 0],
            "instance_id": str(uuid.uuid4()),
        }
        assembly["parts"].append(assembly_part)
        assembly["updated_at"] = datetime.utcnow().isoformat()
        return assembly
    
    def add_mate(
        self, 
        assembly: Dict[str, Any], 
        mate_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a mate between parts."""
        mate = self.mating_engine.create_mate(mate_data)
        assembly["mates"].append(mate)
        assembly["updated_at"] = datetime.utcnow().isoformat()
        return assembly
    
    def validate_assembly(
        self, 
        assembly: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate the assembly."""
        issues = []
        
        # Check for interferences
        interferences = self.interference_checker.check_interferences(assembly)
        if interferences:
            for interference in interferences:
                issues.append(f"Interference: {interference}")
        
        # Check mates
        mate_issues = self.mating_engine.validate_mates(assembly["mates"])
        issues.extend(mate_issues)
        
        return len(issues) == 0, issues
    
    def generate_exploded_view(
        self, 
        assembly: Dict[str, Any],
        direction: Optional[List[float]] = None,
        spacing: float = 50.0
    ) -> Dict[str, Any]:
        """Generate an exploded view of the assembly."""
        exploded = {**assembly}
        dir_vec = direction or [0, 0, 1]
        
        for i, part in enumerate(exploded["parts"]):
            offset = [(i + 1) * spacing * d for d in dir_vec]
            part["exploded_position"] = [
                part["position"][0] + offset[0],
                part["position"][1] + offset[1],
                part["position"][2] + offset[2],
            ]
        
        return exploded


class MatingEngine:
    """Engine for creating and managing mates."""
    
    MATE_TYPES = {
        "coincident": {"description": "Coincident - faces touch"},
        "concentric": {"description": "Concentric - cylinders share axis"},
        "distance": {"description": "Distance - parts separated by distance"},
        "parallel": {"description": "Parallel - faces parallel"},
        "perpendicular": {"description": "Perpendicular - faces perpendicular"},
        "tangent": {"description": "Tangent - faces tangent"},
    }
    
    def create_mate(self, mate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mate constraint."""
        return {
            "id": str(uuid.uuid4()),
            "type": mate_data.get("type", "coincident"),
            "entity1": mate_data.get("entity1"),
            "entity2": mate_data.get("entity2"),
            "parameters": mate_data.get("parameters", {}),
            "created_at": datetime.utcnow().isoformat(),
        }
    
    def validate_mates(self, mates: List[Dict[str, Any]]) -> List[str]:
        """Validate all mates."""
        issues = []
        
        for mate in mates:
            if mate["type"] not in self.MATE_TYPES:
                issues.append(f"Unknown mate type: {mate['type']}")
            if not mate.get("entity1"):
                issues.append(f"Mate missing entity1: {mate['id']}")
            if not mate.get("entity2"):
                issues.append(f"Mate missing entity2: {mate['id']}")
        
        return issues


class InterferenceChecker:
    """Checks for interferences in assemblies."""
    
    def check_interferences(
        self, 
        assembly: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for interferences between parts."""
        interferences = []
        parts = assembly["parts"]
        
        # Check all pairs of parts
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                part1 = parts[i]
                part2 = parts[j]
                
                if self._check_pair_interference(part1, part2):
                    interferences.append({
                        "type": "interference",
                        "part1": part1["instance_id"],
                        "part2": part2["instance_id"],
                        "severity": "medium",
                    })
        
        return interferences
    
    def _check_pair_interference(
        self, 
        part1: Dict[str, Any], 
        part2: Dict[str, Any]
    ) -> bool:
        """Check if two parts interfere (simplified)."""
        # In real implementation, this would use actual geometry
        # For now, just a placeholder
        return False
    
    def check_clearances(
        self, 
        assembly: Dict[str, Any],
        min_clearance: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Check clearances between parts."""
        clearances = []
        parts = assembly["parts"]
        
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                part1 = parts[i]
                part2 = parts[j]
                
                clearance = self._calculate_clearance(part1, part2)
                if clearance < min_clearance:
                    clearances.append({
                        "type": "clearance_issue",
                        "part1": part1["instance_id"],
                        "part2": part2["instance_id"],
                        "clearance": clearance,
                        "min_required": min_clearance,
                    })
        
        return clearances
    
    def _calculate_clearance(
        self, 
        part1: Dict[str, Any], 
        part2: Dict[str, Any]
    ) -> float:
        """Calculate clearance between two parts."""
        # Simplified - in real implementation use geometry
        return 5.0
