"""
Portfolio Manager for Portfolio Module
Manages portfolios.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Manages engineering portfolios.
    """

    def __init__(self):
        self._portfolios: Dict[str, Dict[str, Any]] = {}

    async def create_portfolio(
        self,
        name: str,
        description: str = "",
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        portfolio = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "tenant_id": tenant_id,
            "programs": [],
            "created_at": datetime.utcnow().isoformat(),
        }
        self._portfolios[portfolio["id"]] = portfolio
        return portfolio

    async def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        return self._portfolios.get(portfolio_id)
