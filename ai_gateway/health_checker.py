import os
import aiohttp
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AIHealthChecker:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.tags_url = f"{self.base_url}/api/tags"
        
    async def get_available_models(self) -> List[str]:
        """Fetch list of pulled models on the local AI server."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.tags_url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    return []
        except Exception as e:
            logger.warning(f"Failed to fetch models from AI server: {e}")
            return []

    async def check_health(self) -> Dict[str, Any]:
        """Check if the AI server is reachable and what models are available."""
        models = await self.get_available_models()
        is_healthy = len(models) > 0
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "server": self.base_url,
            "available_models": models,
            "model_count": len(models)
        }

checker = AIHealthChecker()
