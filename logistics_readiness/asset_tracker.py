"""Asset Tracker - Module 8 for Sprint 13."""
from typing import Dict, Any, List, Optional


class AssetTracker:
    def __init__(self):
        self.assets: Dict[str, Dict[str, Any]] = {}

    def register_asset(self, asset_id: str, asset_type: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        self.assets[asset_id] = {
            "id": asset_id,
            "type": asset_type,
            "metadata": metadata or {},
            "status": "idle",
            "last_updated": "",
        }
        return True

    def update_asset_status(self, asset_id: str, status: str, position: Optional[Dict[str, float]] = None) -> bool:
        if asset_id not in self.assets:
            return False
        self.assets[asset_id]["status"] = status
        if position:
            self.assets[asset_id]["position"] = position
        return True

    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.assets.get(asset_id)

    def list_assets(self, asset_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        assets = list(self.assets.values())
        if asset_type:
            assets = [a for a in assets if a["type"] == asset_type]
        if status:
            assets = [a for a in assets if a["status"] == status]
        return assets
