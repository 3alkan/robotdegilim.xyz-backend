import logging
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.context import app_context
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.jobs.scrape_programs import fetch, parse

logger = logging.getLogger(__name__)

def run_scrape_programs() -> None:
    """Run full programs scrape process."""
    settings = get_settings()
    app_context.set({"job_name": "scrape_programs"})
    
    try:
        logger.info("Starting programs scrape job...")
        # TODO: Implement orchestration logic
        
    except Exception as e:
        logger.exception("Programs scrape process failed.")
        if not isinstance(e, AppException):
            raise AppException("Programs scrape process encountered a fatal error.", cause=e)
        raise
    finally:
        app_context.set({})
