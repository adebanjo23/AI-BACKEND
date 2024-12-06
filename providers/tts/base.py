from abc import ABC, abstractmethod
from pydub import AudioSegment

from config.base_config import ProviderConfig


class BaseTTSProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def text_to_speech(self, text: str) -> AudioSegment:
        """Convert text to speech"""
        pass

    async def cleanup(self):
        """Cleanup resources"""
        pass
