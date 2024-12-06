# main.py
import uvicorn
from dotenv import load_dotenv
from config.base_config import BaseConfig, ProviderConfig
from config.prompts.base_prompts import BasePrompts
from providers.stt.deepgram import DeepgramSTT
from providers.llm.groq import GroqLLM
from providers.tts.elevenlabs import ElevenLabsTTS
from pipelines.standard_websocket import StandardWebSocketPipeline
from app.factory import AppFactory
import os

load_dotenv()


def create_websocket_pipeline():
    # Create configuration
    config = BaseConfig()

    # Update TTS config to use ElevenLabs
    config.tts_config = ProviderConfig(
        provider_name="elevenlabs",
        api_key=os.getenv('ELEVENLABS_API_KEY'),
        additional_params={
            'voice_id': os.getenv('ELEVENLABS_VOICE_ID', 'default')  # Replace with your voice ID
        }
    )

    # Configure other providers
    config.stt_config = ProviderConfig(
        provider_name="deepgram",
        api_key=os.getenv('DEEPGRAM_API_KEY'),
        model="nova-2"
    )

    config.llm_config = ProviderConfig(
        provider_name="groq",
        api_key=os.getenv('GROQ_API_KEY'),
        model="llama3-8b-8192"
    )

    config.pipeline_config.pipeline_type = "websocket"

    # Initialize providers
    stt_provider = DeepgramSTT(config.stt_config)
    llm_provider = GroqLLM(config.llm_config)
    tts_provider = ElevenLabsTTS(config.tts_config)

    # Create prompts
    prompts = BasePrompts()
    prompts.update_prompts(
        system_prompt="""You are Santa and you are bringing the Joy and love of the christmas season. 
        Speak in a human, conversational tone. Do not Use Ho-Ho-Ho in your responses.
        Keep your answers as lovely and concise as possible, like in a conversation.
        Note do not use Ho-ho-ho in your responses.
        """
    )

    # Create pipeline
    return StandardWebSocketPipeline(
        stt_provider=stt_provider,
        llm_provider=llm_provider,
        tts_provider=tts_provider,
        config=config,
        prompts=prompts
    )


def main():
    pipeline = create_websocket_pipeline()
    app = AppFactory.create_app(pipeline.config, pipeline)

    # Register routes
    from app.routes import register_routes
    register_routes(app)

    # Run with CORS enabled for frontend access
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()














































# # main.py
# import uvicorn
# from dotenv import load_dotenv
# from config.base_config import BaseConfig, ProviderConfig
# from config.prompts.base_prompts import BasePrompts
# from providers.stt.deepgram import DeepgramSTT
# from providers.llm.groq import GroqLLM
# from providers.tts.deepgram import DeepgramTTS  # Changed from ElevenLabs to Deepgram
# from pipelines.standard_websocket import StandardWebSocketPipeline
# from app.factory import AppFactory
# import os
#
# load_dotenv()
#
#
# def create_websocket_pipeline():
#     # Create configuration
#     config = BaseConfig()
#
#     # Configure STT (Deepgram)
#     config.stt_config = ProviderConfig(
#         provider_name="deepgram",
#         api_key=os.getenv('DEEPGRAM_API_KEY'),
#         model="nova-2"
#     )
#
#     # Configure LLM (Groq)
#     config.llm_config = ProviderConfig(
#         provider_name="groq",
#         api_key=os.getenv('GROQ_API_KEY'),
#         model="llama3-8b-8192"
#     )
#
#     # Configure TTS (Deepgram)
#     config.tts_config = ProviderConfig(
#         provider_name="deepgram",
#         api_key=os.getenv('DEEPGRAM_API_KEY')  # Use the same Deepgram API key
#     )
#
#     config.pipeline_config.pipeline_type = "websocket"
#
#     # Initialize providers
#     stt_provider = DeepgramSTT(config.stt_config)
#     llm_provider = GroqLLM(config.llm_config)
#     tts_provider = DeepgramTTS(config.tts_config)  # Changed to DeepgramTTS
#
#     # Create prompts
#     prompts = BasePrompts()
#     prompts.update_prompts(
#         system_prompt="""You are a helpful and enthusiastic assistant.
#         Speak in a human, conversational tone.
#         Keep your answers as short and concise as possible, like in a conversation,
#         ideally no more than 120 characters."""
#     )
#
#     # Create pipeline
#     return StandardWebSocketPipeline(
#         stt_provider=stt_provider,
#         llm_provider=llm_provider,
#         tts_provider=tts_provider,
#         config=config,
#         prompts=prompts
#     )
#
#
# def main():
#     pipeline = create_websocket_pipeline()
#     app = AppFactory.create_app(pipeline.config, pipeline)
#
#     # Register routes
#     from app.routes import register_routes
#     register_routes(app)
#
#     # Run with CORS enabled for frontend access
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=5050,
#         log_level="info"
#     )
#
#
# if __name__ == "__main__":
#     main()