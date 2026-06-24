"""Environment Builder - Constructs operational environments."""

from typing import Dict, List, Any, Optional
import uuid


class EnvironmentBuilder:
    """Builds operational environments."""
    
    def __init__(self):
        """Initialize environment builder."""
        self.environments: Dict[str, Dict[str, Any]] = {}
    
    def create_environment(
        self,
        name: str,
        environment_type: str,
        bounds: Dict[str, float]
    ) -> str:
        """Create new environment."""
        env_id = str(uuid.uuid4())
        
        self.environments[env_id] = {
            "id": env_id,
            "name": name,
            "type": environment_type,
            "bounds": bounds,  # min_lat, max_lat, min_lon, max_lon
            "terrain": {},
            "obstacles": [],
            "threats": [],
            "weather": {},
        }
        
        return env_id
    
    def add_terrain_data(
        self,
        env_id: str,
        terrain_data: Dict[str, Any]
    ) -> bool:
        """Add terrain data to environment."""
        if env_id not in self.environments:
            return False
        
        self.environments[env_id]["terrain"] = terrain_data
        return True
    
    def add_obstacle(
        self,
        env_id: str,
        obstacle: Dict[str, Any]
    ) -> bool:
        """Add obstacle to environment."""
        if env_id not in self.environments:
            return False
        
        self.environments[env_id]["obstacles"].append(obstacle)
        return True
    
    def add_threat(
        self,
        env_id: str,
        threat: Dict[str, Any]
    ) -> bool:
        """Add threat to environment."""
        if env_id not in self.environments:
            return False
        
        self.environments[env_id]["threats"].append(threat)
        return True
    
    def get_environment(self, env_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve environment."""
        return self.environments.get(env_id)
    
    def list_environments(self) -> List[Dict[str, Any]]:
        """List all environments."""
        return list(self.environments.values())
