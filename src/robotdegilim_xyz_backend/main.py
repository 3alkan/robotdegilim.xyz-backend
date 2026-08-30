from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from robotdegilim_xyz_backend.api.root import router as root_router
from robotdegilim_xyz_backend.api.v1.api import api_router
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.exceptions import AppException, app_exception_handler

settings = get_settings()

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup and shutdown lifecycle hooks for the FastAPI app."""
    # --- Startup Logic ---
    print("Application is starting up... (Placeholder)")
    
    yield
    
    # --- Shutdown Logic ---
    print("Application is shutting down... (Placeholder)")

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
