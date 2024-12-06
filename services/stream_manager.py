import asyncio
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Optional

from pydub import AudioSegment

from providers.tts.base import BaseTTSProvider

class StreamManager:
    def __init__(self, tts_provider: BaseTTSProvider):
        self.current_response_task: Optional[asyncio.Task] = None
        self.should_interrupt: bool = False
        self.lock = asyncio.Lock()
        self.conversation_history: List[Dict[str, str]] = []
        self.current_transcript: str = ""
        self.last_speech_time: float = 0
        self.processing: bool = False
        self.current_tts_task: Optional[asyncio.Task] = None
        self.tts_provider = tts_provider

    @asynccontextmanager
    async def response_context(self):
        async with self.lock:
            if self.current_response_task and not self.current_response_task.done():
                self.should_interrupt = True
                if self.current_tts_task:
                    self.current_tts_task.cancel()
                try:
                    await asyncio.wait_for(self.current_response_task, timeout=0.5)
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    pass
            self.should_interrupt = False
            try:
                yield
            finally:
                self.current_response_task = None
                self.current_tts_task = None

    def add_to_history(self, role: str, content: str):
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)

    async def text_to_speech(self, text: str) -> AudioSegment:
        return await self.tts_provider.text_to_speech(text)