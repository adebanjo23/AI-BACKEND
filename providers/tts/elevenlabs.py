import httpx
from pydub import AudioSegment
import io
from .base import BaseTTSProvider


class ElevenLabsTTS(BaseTTSProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = httpx.AsyncClient()
        self.voice_id = config.additional_params.get('voice_id', 'default')
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"

    async def text_to_speech(self, text: str) -> AudioSegment:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.config.api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "use_speaker_boost": True
            },
            "optimize_streaming_latency": 4
        }

        async with self.client.stream(
                'POST',
                self.url,
                headers=headers,
                json=data
        ) as res:
            audio_data = await res.aread()
            audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
            return audio.set_frame_rate(8000).set_channels(1)

    async def cleanup(self):
        await self.client.aclose()