import httpx
from abc import ABC, abstractmethod
from app.core.config import settings

class LLMProvider(ABC):
    @abstractmethod
    async def invoke(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    async def health_check(self) -> dict:
        pass

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL

    async def invoke(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                # Agent nodes should handle this failure gracefully
                raise RuntimeError(f"OLLAMA_UNAVAILABLE: {str(e)}")

    async def health_check(self) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(self.base_url)
                if response.status_code == 200:
                    return {
                        "status": "ok",
                        "provider": "ollama",
                        "model": self.model
                    }
                return {
                    "status": "error",
                    "code": "OLLAMA_UNAVAILABLE"
                }
            except Exception:
                return {
                    "status": "error",
                    "code": "OLLAMA_UNAVAILABLE"
                }

# Singleton instance for agents to use
llm_provider = OllamaProvider()
