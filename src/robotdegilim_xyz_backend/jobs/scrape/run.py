import logging
from bs4 import BeautifulSoup
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.context import app_context
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.jobs.scrape import fetch, parse
from robotdegilim_xyz_backend.utils.time import get_now_iso_string

logger = logging.getLogger(__name__)

def run_scrape() -> None:
    """Run full scrape process, publish output files directly to S3 memory."""
    settings = get_settings()
    app_context.set({"job_name": "scrape"})
    
    try:
        # Step 1: Initialize session and get main page
        logger.info("Starting scrape job: Fetching main page...")
        main_html = fetch.get_initial_page()
        main_soup = BeautifulSoup(main_html, "html.parser")
        
        # Step 2: Extract dynamic URL for the semester information page
        semester_info_url = parse.extract_semester_info_url(main_soup)
        logger.info(f"Found dynamic semester info URL: {semester_info_url}")
        
        # Step 3: Fetch semester info page
        logger.info("Fetching semester info page...")
        semester_info_html = fetch.get_semester_info_page(semester_info_url)
        semester_info_soup = BeautifulSoup(semester_info_html, "html.parser")
        
        # Step 4: Extract metadata (token, semesters, programs)
        stamp_token = parse.extract_stamp_token(semester_info_soup)
        logger.info("Successfully extracted security stamp token.")
        
        current_semester = parse.extract_current_semester(semester_info_soup)
        programs = parse.extract_programs(semester_info_soup)
        
        # Initialize our master JSON data structure
        final_data = {
            "metadata": {
                "semester_code": current_semester["code"],
                "semester_name": current_semester["name"],
                "updated_at": get_now_iso_string()
            },
            "programs": programs
        }
        
        logger.info(f"Targeting semester: {current_semester['name']} ({current_semester['code']}) with {len(programs)} programs.")

