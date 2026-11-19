"""Entrada e configuração do servidor; dependências montadas em main/factories."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from application.errors import ConflictError, NotFoundError, ValidationError
from main.factories.studio_factory import build_studio
from presentation.controllers.studio_controller import create_studio_router

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC = PROJECT_ROOT / "presentation" / "static"
BASE = Path(os.environ.get("HQ_HOME", str(PROJECT_ROOT))).resolve()


def create_app(base: Path) -> FastAPI:
    container = build_studio(base)

    @asynccontextmanager
    async def lifespan(app):
        yield
        container.generation.executor.shutdown(wait=True)

    app = FastAPI(title="HQ Studio", docs_url="/api/docs", redoc_url=None, lifespan=lifespan)
    app.state.studio = container

    async def application_error(request: Request, exc):
        status = 404 if isinstance(exc, NotFoundError) else 409 if isinstance(exc, ConflictError) else 422
        return JSONResponse(status_code=status, content={"detail": str(exc)})

    for error in (NotFoundError, ConflictError, ValidationError):
        app.add_exception_handler(error, application_error)
    app.include_router(create_studio_router(container.studio))
    app.mount("/media", StaticFiles(directory=container.media.root), name="media")

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app(BASE)
repo = app.state.studio.repo
providers = app.state.studio.providers
service = app.state.studio.generation
MEDIA = app.state.studio.media.root
