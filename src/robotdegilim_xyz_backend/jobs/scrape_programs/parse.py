import logging
from bs4 import BeautifulSoup
from robotdegilim_xyz_backend.core.exceptions import AppException

logger = logging.getLogger(__name__)

def extract_programs_url(soup: BeautifulSoup) -> str:
    """Extracts the dynamic 'Programs' package URL from the main page HTML."""
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if "Programs" == text or "Programs" in text:
            # Check if there is an icon or span with 'title' inside this link
            span = a.find("span", class_="title")
            if span and "Programs" in span.get_text(strip=True):
                return a["href"]
            elif "Programs" == text:
                return a["href"]
                
    raise AppException(
        message="Could not find 'Programs' link on the main page.", 
        code="MISSING_PROGRAMS_LINK"
    )

def extract_stamp_token(soup: BeautifulSoup) -> str:
    """Extracts the hidden CSRF 'stamp' token required for POST requests."""
    stamp_input = soup.find("input", {"name": "stamp", "type": "hidden"})
    
    if not stamp_input or "value" not in stamp_input.attrs:
        raise AppException(
            message="Could not find security 'stamp' token in programs page.", 
            code="MISSING_STAMP_TOKEN"
        )
    return stamp_input["value"]

