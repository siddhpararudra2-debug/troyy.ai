"""
Data Catalog
Catalogs engineering data assets
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DataCatalog:
    """Catalogs data assets"""

    def __init__(self):
        self._assets: Dict[str, Dict[str, Any]] = {}

    async def register_asset(
        self,
        name: str,
        asset_type: str,
        location: str,
    ) -> Dict[str, Any]:
        """Register a data asset"""
        asset_id = str(uuid.uuid4())
        asset = {
            "id": asset_id,
            "name": name,
            "type": asset_type,
            "location": location,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._assets[asset_id] = asset
        logger.info(f"Registered data asset {name}")
        return asset
