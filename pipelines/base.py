from abc import ABC, abstractmethod
from typing import Optional, Any
from providers.stt.base import BaseSTTProvider
from providers.llm.base import BaseLLMProvider
from providers.tts.base import BaseTTSProvider
from config.base_config import BaseConfig
from config.prompts.base_prompts import BasePrompts

class BasePipeline(ABC):
    def __init__(
        self,
        stt_provider: BaseSTTProvider,
        llm_provider: BaseLLMProvider,
        tts_provider: BaseTTSProvider,
        config: BaseConfig,
        prompts: Optional[BasePrompts] = None
    ):
        self.stt = stt_provider
        self.llm = llm_provider
        self.tts = tts_provider
        self.config = config
        self.prompts = prompts or BasePrompts()

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        pass

    async def cleanup(self):
        await self.stt.cleanup()
        await self.llm.cleanup()
        await self.tts.cleanup()