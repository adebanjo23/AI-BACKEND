import json
import base64
import asyncio
import time
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from .base import BasePipeline
from services.stream_manager import StreamManager
from services.audio_handler import AudioHandler


class TwilioPipeline(BasePipeline):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_manager = StreamManager(self.tts)
        self.audio_handler = AudioHandler()
        self.chunk_size = self.config.pipeline_config.chunk_size

    async def process_sentence(self, sentence: str, websocket: WebSocket, stream_sid: str):
        try:
            audio = await self.stream_manager.text_to_speech(sentence)
            chunks = [audio[i:i + self.chunk_size] for i in range(0, len(audio), self.chunk_size)]

            for chunk in chunks:
                if self.stream_manager.should_interrupt:
                    return False
                success, _ = await self.audio_handler.send_audio_chunk(
                    websocket, stream_sid, chunk, self.stream_manager.should_interrupt
                )
                if not success:
                    return False
                await asyncio.sleep(0.05)
            return True
        except asyncio.CancelledError:
            return False

    async def process(self, websocket: WebSocket):
        await websocket.accept()
        stream_sid = None

        async with self.stt.create_connection() as stt_ws:
            async def receive_audio():
                nonlocal stream_sid
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data['event'] == 'media':
                            audio = base64.b64decode(data['media']['payload'])
                            await stt_ws.send(audio)
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            print(f"Stream started: {stream_sid}")
                except WebSocketDisconnect:
                    if stt_ws.open:
                        await stt_ws.close()

            async def handle_responses():
                async for message in stt_ws:
                    transcript_data = await self.stt.process_transcript(message)
                    transcript = transcript_data['transcript']
                    is_final = transcript_data['is_final']

                    if transcript:
                        self.stream_manager.last_speech_time = time.time()

                        if is_final:
                            if not self.stream_manager.current_transcript:
                                self.stream_manager.current_transcript = transcript
                            else:
                                words = transcript.split()
                                current_words = self.stream_manager.current_transcript.split()
                                if len(words) > 0 and words != current_words[-len(words):]:
                                    self.stream_manager.current_transcript += " " + transcript

                            print(f"\rUser: {self.stream_manager.current_transcript}", end='', flush=True)
                        else:
                            print(f"\rUser (typing...): {transcript}", end='', flush=True)

                    if (
                            time.time() - self.stream_manager.last_speech_time > self.config.pipeline_config.speech_timeout and
                            self.stream_manager.current_transcript and not self.stream_manager.processing):
                        self.stream_manager.processing = True
                        print(f"\nProcessing: {self.stream_manager.current_transcript}")

                        async def process_response():
                            try:
                                prompts = self.prompts.get_formatted_prompts(
                                    user_input=self.stream_manager.current_transcript
                                )
                                messages = [
                                    {"role": "system", "content": prompts["system_prompt"]},
                                    {"role": "user", "content": prompts["user_prompt"]}
                                ]

                                ai_response = await self.llm.generate_response(messages)
                                print(f"\nAssistant: {ai_response}")

                                self.stream_manager.current_tts_task = asyncio.create_task(
                                    self.process_sentence(ai_response, websocket, stream_sid)
                                )
                                await self.stream_manager.current_tts_task

                            except asyncio.CancelledError:
                                print("\nResponse interrupted by new input")
                            finally:
                                self.stream_manager.current_transcript = ""
                                self.stream_manager.processing = False

                        async with self.stream_manager.response_context():
                            self.stream_manager.current_response_task = asyncio.create_task(process_response())
                            await self.stream_manager.current_response_task

            await asyncio.gather(receive_audio(), handle_responses())
