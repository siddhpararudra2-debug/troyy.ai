"""
Autoscaling Engine
Manages auto-scaling rules and triggers for services
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AutoscalingEngine:
    """Autoscaling controller for services"""

    def __init__(self):
        self._scaling_rules: Dict[str, Dict[str, Any]] = {}

    async def create_autoscaling_rule(
        self,
        service_name: str,
        min_replicas: int = 1,
        max_replicas: int = 10,
        cpu_threshold: float = 80.0,
    ) -> Dict[str, Any]:
        """Create an auto-scaling rule"""
        rule_id = str(uuid.uuid4())
        rule = {
            "id": rule_id,
            "service_name": service_name,
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "cpu_threshold": cpu_threshold,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._scaling_rules[rule_id] = rule
        logger.info(f"Created auto-scaling rule for {service_name}")
        return rule

    async def get_rules_for_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Get scaling rules for a specific service"""
        return [rule for rule in self._scaling_rules.values() if rule["service_name"] == service_name]
