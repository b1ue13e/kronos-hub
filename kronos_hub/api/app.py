from __future__ import annotations

from fastapi import FastAPI

from kronos_hub.api.routers.engines import router as engines_router
from kronos_hub.api.routers.execution import router as execution_router
from kronos_hub.api.routers.health import router as health_router
from kronos_hub.api.routers.predictions import router as predictions_router
from kronos_hub.api.routers.projects import router as projects_router
from kronos_hub.api.routers.research import router as research_router
from kronos_hub.api.routers.runs import router as runs_router
from kronos_hub.settings import HubSettings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Kronos Hub",
        version="0.1.0",
        description="Integration-first API gateway for ai-hedge-fund, TradingAgents, and Kronos.",
    )

    settings = HubSettings.from_env()

    @app.get("/")
    def root() -> dict:
        return {
            "name": "Kronos Hub",
            "version": "0.1.0",
            "host": settings.host,
            "port": settings.port,
            "docs": "/docs",
        }

    app.include_router(health_router)
    app.include_router(engines_router)
    app.include_router(projects_router)
    app.include_router(runs_router)
    app.include_router(predictions_router)
    app.include_router(research_router)
    app.include_router(execution_router)
    return app


def main() -> None:
    import uvicorn

    settings = HubSettings.from_env()
    uvicorn.run(
        "apps.api_gateway.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
