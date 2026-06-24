"""Command Router - Routes commands to assets and swarms."""

from typing import Dict, List, Any, Optional
from enum import Enum


class CommandRouter:
    """Routes and prioritizes commands to operational assets."""
    
    def __init__(self):
        """Initialize command router."""
        self.routes: Dict[str, List[str]] = {}  # target -> path
        self.priority_queues: Dict[str, List[Dict[str, Any]]] = {}
        self.routing_table: Dict[str, Dict[str, Any]] = {}
    
    def register_asset(self, asset_id: str, asset_type: str, comm_links: List[str]) -> bool:
        """Register asset for command routing."""
        self.routing_table[asset_id] = {
            "type": asset_type,
            "comm_links": comm_links,
            "status": "active",
            "latency": 0.0,
        }
        self.priority_queues[asset_id] = []
        return True
    
    def route_command(
        self,
        command: Dict[str, Any],
        target_id: str,
        priority: int = 5
    ) -> bool:
        """Route command to target asset."""
        if target_id not in self.routing_table:
            return False
        
        route = {
            "command_id": command.get("id"),
            "command_type": command.get("type"),
            "priority": priority,
            "target": target_id,
            "path": self._find_path(target_id),
            "status": "queued",
        }
        
        if target_id in self.priority_queues:
            self.priority_queues[target_id].append(route)
            self.priority_queues[target_id].sort(key=lambda x: x["priority"], reverse=True)
        
        return True
    
    def get_next_command(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get next command for asset from queue."""
        if asset_id not in self.priority_queues:
            return None
        
        if not self.priority_queues[asset_id]:
            return None
        
        command = self.priority_queues[asset_id].pop(0)
        command["status"] = "dispatched"
        return command
    
    def update_asset_status(
        self,
        asset_id: str,
        status: str,
        latency: float = 0.0
    ) -> bool:
        """Update asset status."""
        if asset_id not in self.routing_table:
            return False
        
        self.routing_table[asset_id]["status"] = status
        self.routing_table[asset_id]["latency"] = latency
        
        return True
    
    def get_routing_status(self) -> Dict[str, Any]:
        """Get routing status."""
        total_queued = sum(len(q) for q in self.priority_queues.values())
        active_assets = sum(1 for r in self.routing_table.values() if r["status"] == "active")
        
        return {
            "total_assets": len(self.routing_table),
            "active_assets": active_assets,
            "queued_commands": total_queued,
            "avg_latency": sum(r["latency"] for r in self.routing_table.values()) / len(self.routing_table) if self.routing_table else 0,
        }
    
    def _find_path(self, target_id: str) -> List[str]:
        """Find communication path to target."""
        if target_id in self.routes:
            return self.routes[target_id]
        return [target_id]
