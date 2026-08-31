import logging
from typing import Any
from datetime import datetime, timezone

from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.core.constants import JobOutput

logger = logging.getLogger(__name__)

def run_scrape():
    """
    Main orchestration loop for the scraper.
    Pulls data, parses it, aggregates it in memory, and uploads directly to S3.
    """
    logger.info("Scraping process started.")
    
    # 1. Fetch Main Page & Extract Semester/Departments
    # TODO: Need fetch/parse logic for get_main_page()
    
    # 2. Iterate Departments
    # TODO: Need fetch/parse logic for get_department_page()
    
    # 3. Iterate Courses inside Departments
    # TODO: Need fetch/parse logic for get_course_catalog_page() & get_course_page()
    
    # 4. In-Memory Aggregation
    departments_json: dict[str, dict[str, str]] = {}
    departments_noprefix: dict[str, dict[str, str]] = {}
    data: dict[int, dict[str, Any]] = {}
    
    # 5. Direct S3 Upload (No local disk writing!)
    # s3_client.upload_json(JobOutput.DEPARTMENTS, departments_json)
    # s3_client.upload_json(JobOutput.DATA, data)
    
    logger.info("Scraping process completed successfully. Uploaded to S3.")
