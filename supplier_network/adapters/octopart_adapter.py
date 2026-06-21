import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class OctopartAdapter:
    """Adapter for Octopart API (real component search).
    In production, requires API key from https://octopart.com/api"""
    
    BASE_URL = "https://octopart.com/api/v4/rest"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10.0)
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def search_components(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for electronic components. Returns mock data if no API key."""
        if not self.api_key:
            # Return realistic mock data for development
            return self._mock_search(query, limit)
            
        try:
            response = await self.client.post(
                f"{self.BASE_URL}/search",
                json={"q": query, "limit": limit},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return self._parse_response(response.json())
        except httpx.HTTPError as e:
            raise RuntimeError(f"Octopart API error: {e}")
            
    def _mock_search(self, query: str, limit: int) -> List[Dict]:
        """Realistic mock component data."""
        mock_components = {
            "stm32": [
                {"mpn": "STM32F407VGT6", "manufacturer": "STMicroelectronics",
                 "description": "ARM Cortex-M4 MCU, 168MHz, 1MB Flash",
                 "price_usd": 12.50, "stock": 5420, "lead_time_days": 7},
                {"mpn": "STM32F103C8T6", "manufacturer": "STMicroelectronics",
                 "description": "ARM Cortex-M3 MCU, 72MHz, 64KB Flash",
                 "price_usd": 2.30, "stock": 12500, "lead_time_days": 5},
            ],
            "resistor": [
                {"mpn": "RC0402FR-0710KL", "manufacturer": "Yageo",
                 "description": "10kΩ 1% 0402 Resistor",
                 "price_usd": 0.002, "stock": 1000000, "lead_time_days": 3},
            ],
            "capacitor": [
                {"mpn": "GRM155R71C104KA88D", "manufacturer": "Murata",
                 "description": "100nF 16V X7R 0402 Capacitor",
                 "price_usd": 0.005, "stock": 2000000, "lead_time_days": 3},
            ],
        }
        
        # Find matching mock data
        results = []
        query_lower = query.lower()
        for key, components in mock_components.items():
            if key in query_lower:
                results.extend(components)
                
        # Default fallback
        if not results:
            results = [{
                "mpn": f"PART-{query[:8].upper()}",
                "manufacturer": "Generic",
                "description": f"Component matching '{query}'",
                "price_usd": 1.00,
                "stock": 100,
                "lead_time_days": 14
            }]
            
        return results[:limit]
        
    def _parse_response(self, data: Dict) -> List[Dict]:
        """Parse Octopart API response into normalized format."""
        results = []
        for item in data.get("results", []):
            results.append({
                "mpn": item.get("mpn", ""),
                "manufacturer": item.get("manufacturer", ""),
                "description": item.get("description", ""),
                "price_usd": item.get("price_usd", 0),
                "stock": item.get("stock", 0),
                "lead_time_days": item.get("lead_time_days", 14)
            })
        return results
