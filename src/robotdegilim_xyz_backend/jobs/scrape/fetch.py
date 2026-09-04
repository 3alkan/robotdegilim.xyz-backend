import logging
from robotdegilim_xyz_backend.utils.http import human_client
from robotdegilim_xyz_backend.core.constants import SISConstants

logger = logging.getLogger(__name__)

def get_initial_page() -> str:
    """
    Fetches the main SIS page to establish session cookies and 
    returns the raw HTML containing dynamic package URLs.
    """
    logger.info("Fetching SIS main page to initialize session...")
    response = human_client.get(f"{SISConstants.BASE_URL}/")
    return response.text

def get_semester_info_page(package_url: str) -> str:
    """
    Fetches the specific semester info page using the dynamic package URL.
    This page contains the required CSRF 'stamp' token and program lists.
    """
    logger.info("Fetching semester info page with dynamic route...")
    
    # package_url will look like "get.php?package=UzXQ..."
    url = package_url if package_url.startswith("http") else f"{SISConstants.BASE_URL}/{package_url}"
    
    response = human_client.get(url)
    return response.text
