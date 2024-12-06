import io
import json
import asyncio
import re
import string
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect, WebSocketState
from .base import BasePipeline


class StandardWebSocketPipeline(BasePipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.finish_event = asyncio.Event()

    def should_end_conversation(self, text: str) -> bool:
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.strip().lower()
        return re.search(r'\b(goodbye|bye)\b$', text) is not None

    async def handle_audio_stream(self, websocket: WebSocket):
        try:
            while not self.finish_event.is_set():
                data = await websocket.receive_bytes()
                await self.stt.process_audio(data)
        except Exception as e:
            print(f"Error in handle_audio_stream: {e}")

    async def handle_transcripts(self, websocket: WebSocket):
        while not self.finish_event.is_set():
            try:
                transcript = await self.stt.get_transcript()

                # Send interim or final transcripts to frontend
                await websocket.send_json(transcript)

                # Process final transcripts for AI response
                if transcript['type'] == 'speech_final':
                    if self.should_end_conversation(transcript['content']):
                        self.finish_event.set()
                        await websocket.send_json({'type': 'finish'})
                        break

                    # Generate AI response
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful and enthusiastic assistant. Speak in a human, conversational tone. Keep your answers as short and concise as possible, like in a conversation, ideally no more than 120 characters."
                        },
                        {"role": "user", "content": transcript['content']}
                    ]

                    response = await self.llm.generate_response(messages)

                    # Send text response
                    await websocket.send_json({
                        'type': 'assistant',
                        'content': response
                    })

                    # Generate and stream audio response
                    audio = await self.tts.text_to_speech(response)
                    buffer = io.BytesIO()
                    audio.export(buffer, format="mp3")
                    await websocket.send_bytes(buffer.getvalue())

            except Exception as e:
                print(f"Error in handle_transcripts: {e}")
                if not self.finish_event.is_set():
                    await websocket.send_json({
                        'type': 'error',
                        'message': str(e)
                    })

    async def process(self, websocket: WebSocket):
        await websocket.accept()

        try:
            async with self.stt.create_connection() as connection:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.handle_audio_stream(websocket))
                    tg.create_task(self.handle_transcripts(websocket))
        except* WebSocketDisconnect:
            print('Client disconnected')
        finally:
            self.finish_event.set()
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
            await self.cleanup()
