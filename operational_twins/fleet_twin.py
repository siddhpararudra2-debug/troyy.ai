"""Fleet Twin - Module 7 for Sprint 13."""
from typing import Dict, Any, List
from .operational_twin import OperationalTwin


class FleetTwin:
    def __init__(self, fleet_id: str):
        self.fleet_id = fleet_id
        self.asset_twins: Dict[str, OperationalTwin] = {}
        self.fleet_status: Dict[str, Any] = {
            "total_assets": 0,
            "ready_assets": 0,
            "degraded_assets": 0,
            "unready_assets": 0,
            "readiness_score": 1.0,
        }

    def add_asset_twin(self, asset_twin: OperationalTwin) -> None:
        self.asset_twins[asset_twin.asset_id] = asset_twin
        self._update_fleet_status()

    def remove_asset_twin(self, asset_id: str) -> None:
        if asset_id in self.asset_twins:
            del self.asset_twins[asset_id]
            self._update_fleet_status()

    def _update_fleet_status(self) -> None:
        total = len(self.asset_twins)
        ready = 0
        degraded = 0
        unready = 0
        total_health = 0.0
        
        for twin in self.asset_twins.values():
            health = twin.get_health_status()["health"]
            total_health += health
            if health >= 0.8:
                ready += 1
            elif health >= 0.5:
                degraded += 1
            else:
                unready += 1
        
        self.fleet_status = {
            "total_assets": total,
            "ready_assets": ready,
            "degraded_assets": degraded,
            "unready_assets": unready,
            "readiness_score": total_health / total if total > 0 else 1.0,
        }

    def get_fleet_status(self) -> Dict[str, Any]:
        return self.fleet_status

    def get_all_asset_health(self) -> List[Dict[str, Any]]:
        return [twin.get_health_status() for twin in self.asset_twins.values()]
