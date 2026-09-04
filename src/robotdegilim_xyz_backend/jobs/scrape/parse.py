import logging
from bs4 import BeautifulSoup
from robotdegilim_xyz_backend.core.exceptions import AppException

logger = logging.getLogger(__name__)

def extract_semester_info_url(soup: BeautifulSoup) -> str:
    """
    Extracts the dynamic 'Semester Information' package URL from the main page HTML.
    """
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if "Semester Information" in text:
            return a["href"]
            
    raise AppException(
        message="Could not find 'Semester Information' link on the main page.", 
        code="MISSING_SEMESTER_INFO_LINK"
    )

def extract_stamp_token(soup: BeautifulSoup) -> str:
    """
    Extracts the hidden CSRF 'stamp' token required for POST requests.
    """
    stamp_input = soup.find("input", {"name": "stamp", "type": "hidden"})
    
    if not stamp_input or "value" not in stamp_input.attrs:
        raise AppException(
            message="Could not find security 'stamp' token in course info page.", 
            code="MISSING_STAMP_TOKEN"
        )
    return stamp_input["value"]

def extract_current_semester(soup: BeautifulSoup) -> dict:
    """
    Extracts the current semester from the select options.
    Assumes the current semester is the one with the highest numerical value (e.g. '20261').
    Returns a dictionary with 'code' and 'name'.
    """
    select = soup.find("select", {"name": "selectSemester"})
    if not select:
        raise AppException(
            message="Could not find selectSemester dropdown.", 
            code="MISSING_SEMESTER_SELECT"
        )
        
    current_val = -1
    current_name = ""
    
    for option in select.find_all("option"):
        val = option.get("value")
        if val and val.isdigit():
            val_int = int(val)
            if val_int > current_val:
                current_val = val_int
                current_name = option.get_text(strip=True)
            
    if current_val == -1:
        raise AppException(
            message="Could not find any valid semester values.", 
            code="NO_SEMESTER_VALUES"
        )
        
    return {"code": str(current_val), "name": current_name}

def extract_programs(soup: BeautifulSoup) -> dict:
    """
    Extracts all available programs.
    Returns a dictionary keyed by code:
    {
        "571": {"short_name": "CENG", "name": "Computer Engineering"}
    }
    """
    select = soup.find("select", {"name": "selectProgram"})
    if not select:
        raise AppException(
            message="Could not find selectProgram dropdown.", 
            code="MISSING_PROGRAM_SELECT"
        )
        
    programs = {}
    for option in select.find_all("option"):
        val = option.get("value")
        if val:
            text = option.get_text(strip=True)
            # Text usually looks like "571-CENG-Computer Engineering"
            parts = text.split("-", 2)
            
            if len(parts) == 3:
                short_name = parts[1].strip()
                name = parts[2].strip()
            else:
                # Fallback if the format is unexpected
                logger.warning(f"Unexpected program format for code {val}: '{text}'")
                short_name = "UNKNOWN"
                name = text
                
            programs[val] = {
                "short_name": short_name,
                "name": name
            }
            
    return programs
