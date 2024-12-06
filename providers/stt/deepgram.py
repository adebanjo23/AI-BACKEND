# providers/stt/deepgram.py
from deepgram import (
    DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions
)
from typing import Dict, Any, Optional
import asyncio
from .base import BaseSTTProvider


class DeepgramConnectionManager:
    def __init__(self, provider):
        self.provider = provider
        self.connection = None

    async def __aenter__(self):
        options = LiveOptions(
            model='nova-2',
            language='en',
            smart_format=True,
            interim_results=True,
            utterance_end_ms='1000',
            vad_events=True,
            endpointing=500,
        )

        self.connection = self.provider.client.listen.asynclive.v('1')

        async def on_message(self_handler, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.is_final:
                self.provider.transcript_parts.append(sentence)
                await self.provider.transcript_queue.put({
                    'type': 'transcript_final',
                    'content': sentence,
                    'is_final': True
                })
                if result.speech_final:
                    full_transcript = ' '.join(self.provider.transcript_parts)
                    self.provider.transcript_parts = []
                    await self.provider.transcript_queue.put({
                        'type': 'speech_final',
                        'content': full_transcript,
                        'is_final': True
                    })
            else:
                await self.provider.transcript_queue.put({
                    'type': 'transcript_interim',
                    'content': sentence,
                    'is_final': False
                })

        async def on_utterance_end(self_handler, utterance_end, **kwargs):
            if len(self.provider.transcript_parts) > 0:
                full_transcript = ' '.join(self.provider.transcript_parts)
                self.provider.transcript_parts = []
                await self.provider.transcript_queue.put({
                    'type': 'speech_final',
                    'content': full_transcript,
                    'is_final': True
                })

        self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)

        if await self.connection.start(options) is False:
            raise Exception('Failed to connect to Deepgram')

        self.provider.connection = self.connection
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            await self.connection.finish()
            self.provider.connection = None


class DeepgramSTT(BaseSTTProvider):
    def __init__(self, config):
        super().__init__(config)
        self.client = DeepgramClient(
            config.api_key,
            config=DeepgramClientOptions(options={'keepalive': 'true'})
        )
        self.connection = None
        self.transcript_queue = asyncio.Queue()
        self.transcript_parts = []

    def create_connection(self, **kwargs):
        return DeepgramConnectionManager(self)

    async def process_audio(self, audio_data: bytes):
        if self.connection:
            await self.connection.send(audio_data)

    async def get_transcript(self) -> Dict[str, Any]:
        return await self.transcript_queue.get()

    async def cleanup(self):
        if self.connection:
            await self.connection.finish()
            self.connection = None