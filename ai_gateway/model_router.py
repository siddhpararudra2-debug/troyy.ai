import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ModelRouter:
    """
    Routes inference requests to the appropriate model on the self-hosted AI server.
    Implements fallback logic if a model is unavailable.
    """
    
    def __init__(self):
        self.default_model = os.getenv("DEFAULT_MODEL", "qwen2.5:32b")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "gemma2:9b")
        
        # Capability mapping
        self.capabilities = {
            "coding": ["qwen2.5-coder:32b", "deepseek-coder-v2:16b", self.default_model],
            "reasoning": ["deepseek-r1:14b", "deepseek-r1:32b", self.default_model],
            "general": [self.default_model, self.fallback_model],
            "fast": ["qwen2.5:7b", "gemma2:9b"]
        }

    def route_request(self, task_type: str, requested_model: Optional[str] = None) -> str:
        """
        Determine the best model for the task.
        """
        if requested_model:
            return requested_model
            
        candidates = self.capabilities.get(task_type, self.capabilities["general"])
        
        # In a full implementation, you would check model availability here 
        # (e.g., using health_checker) and select the first available model.
        # For this skeleton, we return the first preferred model.
        
        selected = candidates[0]
        logger.info(f"Routed task '{task_type}' to model: {selected}")
        return selected

router = ModelRouter()
