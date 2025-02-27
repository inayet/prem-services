import argparse
import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as api_router

load_dotenv()

MODEL_PATH = f"./ml/models/{os.getenv('MODEL_ID', 'mistral-7b-instruct-v0.1.Q5_0')}.gguf"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", help="Path to GGUF", default=MODEL_PATH)
    args = parser.parse_args()
    MODEL_PATH = args.model_path

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def create_start_app_handler(app: FastAPI):
    def start_app() -> None:
        from models import LLaMACPPBasedModel

        LLaMACPPBasedModel.get_model(MODEL_PATH)

    return start_app


def get_application() -> FastAPI:
    application = FastAPI(title="prem-chat", debug=True, version="0.0.1")
    application.include_router(api_router, prefix="/v1")
    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return application


app = get_application()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
