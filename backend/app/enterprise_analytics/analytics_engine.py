"""
Analytics Engine for Enterprise Analytics
Central analytics engine.
"""
import logging
from typing import Dict, Any, Optional
from app.enterprise_analytics.metrics_manager import MetricsManager
from app.enterprise_analytics.executive_dashboard import ExecutiveDashboard

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Central orchestrator for enterprise analytics.
    """

    def __init__(self):
        self.metrics = MetricsManager()
        self.dashboard = ExecutiveDashboard()

    async def get_analytics(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive analytics.
        """
        return {
            "tenant_id": tenant_id,
            "executive_dashboard": self.dashboard.get_dashboard(tenant_id),
        }
