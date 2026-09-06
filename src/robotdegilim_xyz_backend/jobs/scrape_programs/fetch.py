import logging
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.utils.http import human_client
from robotdegilim_xyz_backend.core.constants import SISConstants

logger = logging.getLogger(__name__)

def get_initial_page() -> str:
    """Fetch the main SIS landing page to get cookies and module URLs."""
    response = human_client.get(f"{SISConstants.BASE_URL.value}/")
    return response.text

def get_programs_module(package_url: str) -> str:
    """Load the Programs module using its dynamic package URL to get the stamp."""
    url = f"{SISConstants.BASE_URL.value}/{package_url}"
    response = human_client.get(url)
    return response.text

def add_campus_filter(stamp: str) -> str:
    """Add the Campus filter box to the UI session."""
    payload = {
        "selectField[]": "selectCampus",
        "stamp": stamp,
        "submitFilter": "Update"
    }
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    response = human_client.post(f"{SISConstants.BASE_URL.value}/main.php", data=payload, headers=headers)
    return response.text

def search_all_programs(stamp: str) -> str:
    """Search for all programs across Campuses 1 and 2."""
    # Note: requests/curl_cffi handles lists by repeating the key if we pass a list of tuples, 
    # but to be safe and perfectly match the payload `selectCampus[]=1&selectCampus[]=2`:
    payload = [
        ("selectCampus[]", "1"),
        ("selectCampus[]", "2"),
        ("submitSearchForm", "Search"),
        ("stamp", stamp)
    ]
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }
    response = human_client.post(f"{SISConstants.BASE_URL.value}/main.php", data=payload, headers=headers)
    
    try:
        json_data = response.json()
        return json_data.get("data", "")
    except Exception as e:
        logger.error(f"search_all_programs failed to decode JSON. Response: {response.text[:200]}")
        raise AppException("Failed to decode programs search response.", cause=e)

def fetch_program_details(stamp: str, program_key: str) -> str:
    """Fetch the specific program details page using its key (e.g. 120|1|1|1)."""
    payload = {
        "submitTableClick": "1",
        "textTableKeys": program_key,
        "stamp": stamp
    }
    # Important: This is a direct FORM POST, not an AJAX request.
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = human_client.post(f"{SISConstants.BASE_URL.value}/main.php", data=payload, headers=headers)
    return response.text

