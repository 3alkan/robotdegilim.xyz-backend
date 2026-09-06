import logging
from bs4 import BeautifulSoup
from robotdegilim_xyz_backend.core.exceptions import AppException

logger = logging.getLogger(__name__)

def to_float(val: str) -> float:
    """Helper to safely convert Turkish string numbers to float."""
    try:
        return float(val.strip().replace(',', '.')) if val.strip() else 0.0
    except ValueError:
        return 0.0

def to_int(val: str) -> int:
    """Helper to safely convert string numbers to int."""
    try:
        return int(float(val.strip().replace(',', '.'))) if val.strip() else 0
    except ValueError:
        return 0


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

def extract_courses(soup: BeautifulSoup) -> dict:
    """
    Parses the massive HTML table returned by the POST request.
    Uses dynamic header mapping to prevent hardcoded column index errors.
    Groups multiple rows by course and section to produce a nested JSON structure.
    """
    table = soup.find("table", {"id": "SearchResults"})
    if not table:
        logger.warning("No SearchResults table found. It might be an empty department.")
        return []
        
    thead = table.find("thead")
    tbody = table.find("tbody")
    if not thead or not tbody:
        return []
        
    # Dynamically build column mapping: {"Course Code": 4, "Capacity": 12, ...}
    headers = thead.find_all("th")
    col_map = {th.get_text(strip=True): idx for idx, th in enumerate(headers)}
            
    courses_dict = {}
    
    for row in tbody.find_all("tr"):
        cols = row.find_all("td")
        if not cols:
            continue
            
        tds = [td.get_text(strip=True) for td in cols]
        
        # Safely convert the row into a key-value dictionary using the dynamic col_map
        row_data = {name: (tds[idx] if idx < len(tds) else "") for name, idx in col_map.items()}
        
        course_code = row_data.get("Course Code")
        if not course_code:
            continue
            
        if course_code not in courses_dict:
            courses_dict[course_code] = {
                "code": course_code,
                "name": row_data.get("Course Name", ""),
                "credits": {
                    "total": to_float(row_data.get("Credit", "")),
                    "ects": to_float(row_data.get("ECTS Credit", "")),
                    "lab": to_float(row_data.get("Laboratory Credit", "")),
                    "theory": to_float(row_data.get("Theory Credit", "")),
                    "application": to_float(row_data.get("Application Credit", ""))
                },
                "is_service_course": row_data.get("Service Course", "").lower() == "yes",
                "level": row_data.get("Course Level", ""),
                "type": row_data.get("Course Type", ""),
                "sections": {}
            }
            
        course_obj = courses_dict[course_code]
        section_num_str = row_data.get("Course Section", "")
        if not section_num_str:
            continue
            
        section_num = to_int(section_num_str)
        if section_num not in course_obj["sections"]:
            course_obj["sections"][section_num] = {
                "section_number": section_num,
                "capacity": {
                    "total": to_int(row_data.get("Capacity", "")),
                    "exchange": to_int(row_data.get("Exchange Capacity", "")),
                    "exchange_used": to_int(row_data.get("Exchange Used Capacity", ""))
                },
                "schedule": [],
                "instructors": [],
                "criteria": []
            }
            
        section_obj = course_obj["sections"][section_num]
        
        # 1. Extract up to 5 schedule blocks (Columns like Day1, Day2, etc.)
        for i in range(1, 6):
            day = row_data.get(f"Day{i}")
            if day:
                sched_item = {
                    "day": day,
                    "start_hour": row_data.get(f"Start Hour{i}", ""),
                    "end_hour": row_data.get(f"End Hour{i}", ""),
                    "classroom": row_data.get(f"Classroom {i}", ""),
                    "building": row_data.get(f"Classroom Building {i}", "")
                }
                if sched_item not in section_obj["schedule"]:
                    section_obj["schedule"].append(sched_item)
                    
        # 2. Extract Instructors
        inst_name = row_data.get("Instructor Name")
        if inst_name:
            inst_item = {
                "name": inst_name,
                "title": row_data.get("Instructor Title", "")
            }
            if inst_item not in section_obj["instructors"]:
                section_obj["instructors"].append(inst_item)
                
        # 3. Extract Criteria
        given_dept = row_data.get("Given Dept Name")
        if given_dept or row_data.get("Start Char") or row_data.get("Min CumGPA") or row_data.get("Start Grade"):
            crit_item = {
                "given_dept": given_dept or "",
                "start_char": row_data.get("Start Char", ""),
                "end_char": row_data.get("End Char", ""),
                "cgpa": {
                    "min": to_float(row_data.get("Min CumGPA", "")), 
                    "max": to_float(row_data.get("Max CumGPA", ""))
                },
                "year": {
                    "min": to_int(row_data.get("Min Year", "")), 
                    "max": to_int(row_data.get("Max Year", ""))
                },
                "start_grade": row_data.get("Start Grade", ""),
                "end_grade": row_data.get("End Grade", "")
            }
            if crit_item not in section_obj["criteria"]:
                section_obj["criteria"].append(crit_item)
                
    return courses_dict

