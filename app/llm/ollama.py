import requests

from app.core.config import settings


class OllamaProvider:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
    ):
        self.model = model or settings.ollama_model
        self.base_url = (
            base_url or settings.ollama_base_url
        ).rstrip("/")

    def generate(
        self,
        prompt: str,
    ) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]