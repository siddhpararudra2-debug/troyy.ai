"""
Plugin Registry Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class PluginRegistry:
    def __init__(self):
        self.plugins: Dict[str, Dict[str, Any]] = {}

    def register_plugin(self, plugin_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        plugin_id = str(uuid.uuid4())
        plugin = {
            "id": plugin_id,
            **plugin_data,
            "registered_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }
        self.plugins[plugin_id] = plugin
        return plugin

    def list_registered_plugins(self) -> List[Dict[str, Any]]:
        start_time = time.time()
        return list(self.plugins.values())
