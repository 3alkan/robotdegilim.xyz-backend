import logging
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.utils.http import human_client
from robotdegilim_xyz_backend.core.constants import SISConstants

logger = logging.getLogger(__name__)

def get_initial_page() -> str:
    """
    Fetches the main SIS page to establish session cookies and 
    returns the raw HTML containing dynamic package URLs.
    """
    logger.info("Fetching SIS main page to initialize session...")
    response = human_client.get(f"{SISConstants.BASE_URL.value}/")
    return response.text

def get_semester_info_page(package_url: str) -> str:
    """
    Fetches the specific semester info page using the dynamic package URL.
    This page contains the required CSRF 'stamp' token and program lists.
    """
    logger.info("Fetching semester info page with dynamic route...")
    
    # package_url will look like "get.php?package=UzXQ..."
    url = package_url if package_url.startswith("http") else f"{SISConstants.BASE_URL.value}/{package_url}"
    
    response = human_client.get(url)
    return response.text

def fetch_program_courses(semester_code: str, program_code: str, stamp_token: str) -> str:
    """
    Sends a POST request to search for all courses in a specific program and semester.
    Returns the raw HTML table string extracted from the JSON response.
    """
    logger.info(f"Fetching courses for program {program_code}...")
    
    payload = {
        "selectCourseCriteriaType": "",
        "selectSemester": semester_code,
        "selectProgram": program_code,
        "submitSearchForm": "Search",
        "stamp": stamp_token
    }
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    
    response = human_client.post(
        f"{SISConstants.BASE_URL.value}/main.php", 
        data=payload,
        headers=headers
    )
    json_data = response.json()
    
    if json_data.get("error"):
        raise AppException(
            message=f"Failed to fetch courses for program {program_code}", 
            code="FETCH_COURSES_ERROR"
        )
        
    return json_data.get("data", "")
