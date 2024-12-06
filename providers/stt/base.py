# providers/stt/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseSTTProvider(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    async def create_connection(self, **kwargs):
        """Create a connection to the STT service"""
        pass

    @abstractmethod
    async def process_audio(self, audio_data: bytes):
        """Process audio data"""
        pass

    @abstractmethod
    async def get_transcript(self) -> Dict[str, Any]:
        """Get transcript from the queue"""
        pass

    async def cleanup(self):
        """Cleanup resources"""
        pass