import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from robotdegilim_xyz_backend.api.root import router as root_router
from robotdegilim_xyz_backend.api.v1.api import api_router
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.exceptions import AppException, app_exception_handler
from robotdegilim_xyz_backend.core.logging import setup_logging

settings = get_settings()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup and shutdown lifecycle hooks for the FastAPI app."""
    # Setup global standard logging format
    setup_logging()
    
    logger.info("Application is starting up...")
    yield
    logger.info("Application is shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Register Global Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the root discovery router (no prefix)
app.include_router(root_router)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)
