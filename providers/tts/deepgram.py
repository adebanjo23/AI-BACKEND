import httpx
from pydub import AudioSegment
import io
from .base import BaseTTSProvider


class DeepgramTTS(BaseTTSProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = httpx.AsyncClient()
        self.url = 'https://api.deepgram.com/v1/speak?model=aura-luna-en'

    async def text_to_speech(self, text: str) -> AudioSegment:
        headers = {
            'Authorization': f'Token {self.config.api_key}',
            'Content-Type': 'application/json'
        }

        async with self.client.stream(
                'POST',
                self.url,
                headers=headers,
                json={'text': text}
        ) as res:
            audio_data = await res.aread()
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            return audio.set_frame_rate(8000).set_channels(1)

    async def cleanup(self):
        await self.client.aclose()