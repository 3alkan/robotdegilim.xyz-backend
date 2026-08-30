from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from robotdegilim_xyz_backend.api.v1.api import api_router
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.exceptions import AppException, app_exception_handler

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for robotdegilim.xyz",
    version=settings.VERSION,
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

# Include the main API router
app.include_router(api_router, prefix="/api/v1")
