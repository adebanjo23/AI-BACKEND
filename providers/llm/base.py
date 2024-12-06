from abc import ABC, abstractmethod
from typing import Dict, Any, List

from config.base_config import ProviderConfig


class BaseLLMProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from messages"""
        pass

    async def cleanup(self):
        """Cleanup resources"""
        pass
