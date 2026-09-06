import logging
from bs4 import BeautifulSoup
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
        logger.info("Starting programs scrape job: Fetching main page...")
        main_html = fetch.get_initial_page()
        main_soup = BeautifulSoup(main_html, "html.parser")
        
        programs_url = parse.extract_programs_url(main_soup)
        
        logger.info("Loading Programs module to get security stamp...")
        programs_html = fetch.get_programs_module(programs_url)
        programs_soup = BeautifulSoup(programs_html, "html.parser")
        stamp = parse.extract_stamp_token(programs_soup)
        
        logger.info("Injecting Campus filter UI...")
        fetch.add_campus_filter(stamp)
        
        logger.info("Searching for all active programs across campuses...")
        programs_json_html = fetch.search_all_programs(stamp)
        programs_table_soup = BeautifulSoup(programs_json_html, "html.parser")
        
        
    except Exception as e:
        logger.exception("Programs scrape process failed.")
        if not isinstance(e, AppException):
            raise AppException("Programs scrape process encountered a fatal error.", cause=e)
        raise
    finally:
        app_context.set({})
