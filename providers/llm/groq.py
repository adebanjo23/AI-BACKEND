from groq import AsyncGroq
from typing import List, Dict
from .base import BaseLLMProvider

class GroqLLM(BaseLLMProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = AsyncGroq(api_key=config.api_key)

    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7)
        )
        return response.choices[0].message.content