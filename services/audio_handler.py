import base64
import io
import json
import asyncio
from typing import Tuple
from pydub import AudioSegment

class AudioHandler:
    @staticmethod
    async def send_audio_chunk(websocket, stream_sid: str, chunk: AudioSegment, should_interrupt: bool) -> Tuple[bool, float]:
        if should_interrupt:
            return False, 0

        buffer = io.BytesIO()
        chunk.export(buffer, format="wav", parameters=["-acodec", "pcm_mulaw"])
        audio_data = buffer.getvalue()

        await websocket.send_text(json.dumps({
            "event": "media",
            "streamSid": stream_sid,
            "media": {
                "payload": base64.b64encode(audio_data).decode('utf-8')
            }
        }))
        return True, 0