import os
import aiohttp
import json
import logging
from typing import AsyncGenerator, Dict, Any

logger = logging.getLogger(__name__)

class InferenceClient:
    """
    Client to communicate with the local Ollama API for model inference.
    """
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.api_generate = f"{self.base_url}/api/generate"
        self.api_chat = f"{self.base_url}/api/chat"

    async def generate_stream(self, model: str, prompt: str, system: str = "") -> AsyncGenerator[str, None]:
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_generate, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    response.raise_for_status()
                    async for line in response.content:
                        if line:
                            data = json.loads(line.decode('utf-8'))
                            yield data.get("response", "")
        except Exception as e:
            logger.error(f"Inference error with model {model}: {str(e)}")
            raise

    async def chat(self, model: str, messages: list[Dict[str, str]]) -> Dict[str, Any]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_chat, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as e:
            logger.error(f"Chat error with model {model}: {str(e)}")
            raise

client = InferenceClient()
