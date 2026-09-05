"""Composition root: Construction of the Application / API."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from what_to_do.api.errors import ERROR_STATUS_CODES
from what_to_do.api.health import router as health_check
from what_to_do.api.v1.groups import router as group_router
from what_to_do.api.v1.projects import router as project_router
from what_to_do.api.v1.tasks import router as task_router
from what_to_do.core.settings import get_settings
from what_to_do.db.database import get_engine
from what_to_do.db.schema import Base

type ExceptionHandler = Callable[[Request, Exception], JSONResponse]

# fetch configuration (from environment variables)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Initialize application resources on startup"""
    Base.metadata.create_all(bind=get_engine())
    yield


def create_exception_handler(status_code: int) -> ExceptionHandler:
    """Create a function to use FastAPI's builtin mechanism for adding exception handlers."""

    def handler(_: Request, exc: Exception) -> JSONResponse:
        """Convert domain error into HTML response (JSON)."""
        message = str(exc)
        return JSONResponse(
            status_code=status_code,
            content={
                "error": type(exc).__name__,
                "detail": message,
            },
        )

    return handler


def create_app() -> FastAPI:
    """Create FastAPI backend application"""

    # compose application
    app = FastAPI(
        title=settings.app_name,
        version=settings.backend_api_version,
        lifespan=lifespan,
    )

    # register routers
    app.include_router(health_check)
    app.include_router(task_router, prefix=f"{settings.api_url_prefix}/tasks")
    app.include_router(project_router, prefix=f"{settings.api_url_prefix}/projects")
    app.include_router(group_router, prefix=f"{settings.api_url_prefix}/groups")

    # register exception handlers
    for error, status_code in ERROR_STATUS_CODES.items():
        app.add_exception_handler(error, handler=create_exception_handler(status_code))

    return app


# Expose application (needed to setup backend using Docker)
app = create_app()

# Serve application if run directly
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)
