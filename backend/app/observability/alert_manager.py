"""
Alert Manager
Manages system alerts
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages system alerts"""

    def __init__(self):
        self._alerts: List[Dict[str, Any]] = []

    async def trigger_alert(
        self,
        alert_type: str,
        message: str,
        severity: str,
    ) -> Dict[str, Any]:
        """Trigger an alert"""
        alert_id = str(uuid.uuid4())
        alert = {
            "id": alert_id,
            "type": alert_type,
            "message": message,
            "severity": severity,
            "triggered_at": datetime.utcnow().isoformat(),
        }
        self._alerts.append(alert)
        logger.warning(f"Triggered alert: {message} (severity: {severity})")
        return alert
