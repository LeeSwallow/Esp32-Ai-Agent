from fastapi import FastAPI

from app.util.db import Base, engine
from app.router.api import router as api_router
from app.router.ws import router as ws_router


def create_app() -> FastAPI:
    # Create tables if not exist (MVP)
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="tts-arduino-server", version="0.1.0")

    app.include_router(api_router)
    app.include_router(ws_router)

    return app


app = create_app()


