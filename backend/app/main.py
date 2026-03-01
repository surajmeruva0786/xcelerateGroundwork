from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.scheduler import start_scheduler
from app.routers import analysis, plots, runs


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)

    # CORS
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Routers
    app.include_router(
        analysis.router, prefix=settings.API_V1_STR + "/analysis", tags=["analysis"]
    )
    app.include_router(
        plots.router, prefix=settings.API_V1_STR + "/plots", tags=["plots"]
    )
    app.include_router(
        runs.router, prefix=settings.API_V1_STR + "/analysis", tags=["analysis"]
    )

    # Start background scheduler
    start_scheduler()

    return app


app = create_app()


