from fastapi import APIRouter
from robotdegilim_xyz_backend.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/", tags=["Discovery"])
def api_discovery():
    """
    Root endpoint providing API discovery and metadata.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": settings.PROJECT_DESCRIPTION,
        "links": {
            "self": "/",
            "docs": "/docs",
            "health": f"{settings.API_V1_STR}/health",
            "scrape_courses": f"{settings.API_V1_STR}/jobs/scrape_courses",
            "scrape_programs": f"{settings.API_V1_STR}/jobs/scrape_programs"
        }
    }
