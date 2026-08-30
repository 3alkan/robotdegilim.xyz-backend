from fastapi import APIRouter
from robotdegilim_xyz_backend.api.v1.endpoints import health, jobs

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
