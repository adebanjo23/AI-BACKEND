from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class ProviderConfig:
    provider_name: str
    model: Optional[str] = None
    api_key: Optional[str] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineConfig:
    pipeline_type: str  # "twilio" or "websocket"
    chunk_size: int = 8000
    speech_timeout: float = 0.1
    additional_params: Dict[str, Any] = field(default_factory=dict)


class BaseConfig:
    def __init__(self):
        # Load environment variables
        self.stt_config = ProviderConfig(
            provider_name="deepgram",
            api_key=os.getenv('DEEPGRAM_API_KEY'),
            model="nova-2"
        )

        self.llm_config = ProviderConfig(
            provider_name="groq",
            api_key=os.getenv('GROQ_API_KEY'),
            model="llama3-8b-8192"
        )

        self.tts_config = ProviderConfig(
            provider_name="deepgram",
            api_key=os.getenv('DEEPGRAM_API_KEY')
        )

        self.pipeline_config = PipelineConfig(
            pipeline_type="twilio",
            chunk_size=8000,
            speech_timeout=0.1
        )

    def update_stt_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.stt_config, key):
                setattr(self.stt_config, key, value)

    def update_llm_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.llm_config, key):
                setattr(self.llm_config, key, value)

    def update_tts_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.tts_config, key):
                setattr(self.tts_config, key, value)

    def update_pipeline_config(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self.pipeline_config, key):
                setattr(self.pipeline_config, key, value)