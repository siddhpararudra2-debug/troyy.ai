"""
Portfolio Management Service
"""
import uuid
import time
from typing import Dict, Any, List
from datetime import datetime


class PortfolioManagementService:
    def __init__(self):
        self.portfolios: Dict[str, Dict[str, Any]] = {}

    def create_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        portfolio_id = str(uuid.uuid4())
        portfolio = {
            "id": portfolio_id,
            **portfolio_data,
            "created_at": datetime.utcnow().isoformat(),
            "execution_time_ms": (time.time() - start_time) * 1000
        }
        self.portfolios[portfolio_id] = portfolio
        return portfolio

    def get_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        start_time = time.time()
        return self.portfolios.get(portfolio_id, {})

    def list_portfolios(self) -> List[Dict[str, Any]]:
        start_time = time.time()
        return list(self.portfolios.values())
