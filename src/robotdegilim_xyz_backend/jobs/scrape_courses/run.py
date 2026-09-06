import logging
from bs4 import BeautifulSoup
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.core.context import app_context
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.jobs.scrape_courses import fetch, parse
from robotdegilim_xyz_backend.utils.time import get_now_iso_string
from robotdegilim_xyz_backend.schemas.scrape_data import ScrapeData
from robotdegilim_xyz_backend.core.constants import S3Prefix

logger = logging.getLogger(__name__)

def run_scrape_courses() -> None:
    """Run full scrape courses process, publish output files directly to S3 memory."""
    settings = get_settings()
    app_context.set({"job_name": "scrape_courses"})
    
    try:
        # Step 1: Initialize session and get main page
        logger.info("Starting scrape courses job: Fetching main page...")
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

        # Step 5: Iterate over programs and fetch their table data via POST requests
        for dept_code in final_data["programs"].keys():
            html_table = fetch.fetch_program_courses(
                semester_code=current_semester["code"], 
                program_code=dept_code, 
                stamp_token=stamp_token
            )
            table_soup = BeautifulSoup(html_table, "html.parser")
            
            # Extract and parse the courses
            courses = parse.extract_courses(table_soup)
            final_data["programs"][dept_code]["courses"] = courses
            
        logger.info(f"Scrape job completed successfully for {len(final_data['programs'])} programs.")
        
        # Validate the entire structured dictionary against our Pydantic schema
        validated_data = ScrapeData(**final_data)
        logger.info("Data successfully validated through Pydantic! No structural errors found.")
        
        # Convert the Pydantic object back into a clean, validated dictionary
        clean_payload = validated_data.model_dump()
        
        # Save to a single, authoritative endpoint for the current semester
        live_key = f"{S3Prefix.DATA.value}scrape_courses/{current_semester['code']}.json"
        s3_client.upload_json(live_key, clean_payload)
        
        logger.info(f"Live data successfully updated on S3: {live_key}")
        
    except Exception as e:
        logger.exception("Scrape process failed.")
        # If it's not an AppException already, wrap it so the structured logger catches it beautifully
        if not isinstance(e, AppException):
            raise AppException("Scrape process encountered a fatal error.", cause=e)
        raise
    finally:
        app_context.set({})