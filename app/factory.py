from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.base_config import BaseConfig
from pipelines.base import BasePipeline


class AppFactory:
    @staticmethod
    def create_app(config: BaseConfig, pipeline: BasePipeline) -> FastAPI:
        app = FastAPI()

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Store config and pipeline in app state
        app.state.config = config
        app.state.pipeline = pipeline

        return app
