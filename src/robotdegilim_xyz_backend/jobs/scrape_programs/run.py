import logging
import datetime
from bs4 import BeautifulSoup
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.context import app_context
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.jobs.scrape_programs import fetch, parse
from robotdegilim_xyz_backend.schemas.scrape_programs_data import ScrapeProgramsData, ProgramDetails

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
        
        program_keys = parse.extract_program_keys(programs_table_soup)
        
        logger.info(f"Successfully extracted {len(program_keys)} programs to process.")
        
        # Extract the initial stamp from the search results JSON (it contains an HTML form at the end)
        current_stamp = parse.extract_stamp_token(programs_table_soup)
        
        final_programs = {}
        for index, prog_meta in enumerate(program_keys):
            p_key = prog_meta["program_key"]
            logger.info(f"[{index+1}/{len(program_keys)}] Fetching details for program: {p_key}")
            
            detail_html = fetch.fetch_program_details(current_stamp, p_key)
            
            parsed_details = parse.parse_program_details(detail_html)
            
            # Extract the new stamp from this detail page for the next request
            try:
                detail_soup = BeautifulSoup(detail_html, "html.parser")
                current_stamp = parse.extract_stamp_token(detail_soup)
            except Exception as e:
                logger.warning(f"Could not extract new stamp from {p_key}, falling back to old stamp. Error: {e}")
            
            # Merge list response metadata with detailed metadata
            merged = {**prog_meta, **parsed_details}
            
            # Validate through Pydantic
            try:
                program_model = ProgramDetails(**merged)
                final_programs[p_key] = program_model
            except Exception as e:
                logger.error(f"Failed to validate ProgramDetails for {p_key}: {e}")
                
        # Create final root model
        final_data = ScrapeProgramsData(
            updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            programs=final_programs
        )
        
        # Upload to S3
        logger.info("Uploading final programs.json to S3...")
        s3_client.upload_json("data/scrape_programs/programs.json", final_data.model_dump(mode='json'), public_read=True)
        logger.info("Successfully finished programs scrape job.")
        
    except Exception as e:
        logger.exception("Programs scrape process failed.")
        if not isinstance(e, AppException):
            raise AppException("Programs scrape process encountered a fatal error.", cause=e)
        raise
    finally:
        app_context.set({})
