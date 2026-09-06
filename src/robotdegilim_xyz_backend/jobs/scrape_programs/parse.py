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

def extract_program_keys(soup: BeautifulSoup) -> list[dict]:
    """
    Parses the massive HTML table of programs to extract their table keys.
    Returns a list of dicts with all metadata columns.
    """
    table = soup.find("table", {"id": "SearchResultsProgram"})
    if not table:
        raise AppException("No SearchResultsProgram table found in programs search response.", code="NO_PROGRAMS_TABLE")
        
    tbody = table.find("tbody")
    if not tbody:
        return []
        
    programs = []
    
    for row in tbody.find_all("tr"):
        # The hidden key is stored in the key attribute of the row: e.g. <tr key="571|1|1|1">
        program_key = row.get("key", "")
        if not program_key:
            continue
            
        cols = row.find_all("td")
        if len(cols) < 12:
            continue
            
        tds = [td.get_text(strip=True) for td in cols]
        
        # Column 0: Campus Long Name
        # Column 1: Campus Short Name
        # Column 2: Program Code
        # Column 3: Department Code
        # Column 4: Program Short Name
        # Column 5: Program Long Name Eng
        # Column 6: Program Type
        # Column 7: Faculty
        # Column 8: Institute
        # Column 9: Education Type
        # Column 10: Education Level
        # Column 11: Program Administrator
        
        programs.append({
            "program_key": program_key,
            "campus_long_name": tds[0] if len(tds) > 0 else "",
            "campus_short_name": tds[1] if len(tds) > 1 else "",
            "program_code": tds[2] if len(tds) > 2 else "",
            "department_code": tds[3] if len(tds) > 3 else "",
            "short_name": tds[4] if len(tds) > 4 else "",
            "long_name": tds[5] if len(tds) > 5 else "",
            "program_type": tds[6] if len(tds) > 6 else "",
            "faculty_name": tds[7] if len(tds) > 7 else "",
            "institute_name": tds[8] if len(tds) > 8 else "",
            "education_type": tds[9] if len(tds) > 9 else "",
            "education_level": tds[10] if len(tds) > 10 else "",
            "administrator": tds[11] if len(tds) > 11 else "",
        })
        
    return programs

def _extract_infobox_value(soup: BeautifulSoup, label_text: str) -> str:
    """Helper to extract a value from a cc-infobox given its label text."""
    label = soup.find("span", class_="cc-infobox-label", string=lambda s: s and label_text in s)
    if label:
        info_span = label.find_next_sibling("span", class_="cc-infobox-info")
        if info_span:
            return info_span.get_text(strip=True)
    return ""

def parse_program_details(html: str) -> dict:
    """Parses the specific program details HTML into the final nested dictionary."""
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. OSYM Code
    osym_code = _extract_infobox_value(soup, "OSYM Code")
    
    # 2. Program Summary
    min_credit_str = _extract_infobox_value(soup, "Minimum Total Credit")
    min_credit = float(min_credit_str) if min_credit_str else 0.0
    
    overload_str = _extract_infobox_value(soup, "Overload")
    overload = float(overload_str) if overload_str else 0.0
    
    degree = _extract_infobox_value(soup, "Degree")
    
    min_duration_str = _extract_infobox_value(soup, "Minimum Duration")
    min_duration = int(min_duration_str) if min_duration_str else 0
    
    max_duration_str = _extract_infobox_value(soup, "Maximum Duration")
    max_duration = int(max_duration_str) if max_duration_str else 0
    
    # 3. Curriculum
    curriculum = {}
    pcid_tab = soup.find("div", {"id": "pcid"})
    if pcid_tab:
        semesters = pcid_tab.find_all("div", class_="box-table-curriculum")
        for sem in semesters:
            sem_header = sem.find("div", class_="box-table-head-curriculum")
            if not sem_header:
                continue
            sem_title = sem_header.get_text(strip=True)
            # Extracts '1' from '1.Semester'
            import re
            match = re.search(r"(\d+)", sem_title)
            if not match:
                continue
            sem_num = int(match.group(1))
            
            courses = []
            rows = sem.find_all("div", class_="box-row-curriculum")
            for row in rows:
                code_div = row.find("div", class_="box-column-label-curriculum")
                val_div = row.find("div", class_="box-column-value-curriculum")
                if not code_div or not val_div:
                    continue
                
                code = code_div.get_text(strip=True)
                # val_div has 3 inner divs: name, metu_credit, ects_credit
                inner_divs = val_div.find_all("div", recursive=False)
                if len(inner_divs) >= 3:
                    name = inner_divs[0].get_text(strip=True)
                    try:
                        metu_credit = float(inner_divs[1].get_text(strip=True))
                    except ValueError:
                        metu_credit = 0.0
                    try:
                        ects_credit = float(inner_divs[2].get_text(strip=True))
                    except ValueError:
                        ects_credit = 0.0
                        
                    is_elective = not bool(code) or "ELECTIVE" in name.upper() or "SEÇMELİ" in name.upper()
                    
                    courses.append({
                        "code": code,
                        "name": name,
                        "metu_credit": metu_credit,
                        "ects_credit": ects_credit,
                        "is_elective": is_elective
                    })
            
            curriculum[sem_num] = {
                "semester_number": sem_num,
                "courses": courses
            }
            
    # 4. Electives
    electives = []
    electives_table = soup.find("table", {"id": "SearchProgramElectiveCourse"})
    if electives_table:
        tbody = electives_table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) >= 3:
                    electives.append({
                        "code": tds[0].get_text(strip=True),
                        "name": tds[1].get_text(strip=True),
                        "category": tds[2].get_text(strip=True)
                    })
                    
    return {
        "osym_code": osym_code,
        "minimum_total_credit": min_credit,
        "overload": overload,
        "degree": degree,
        "minimum_duration": min_duration,
        "maximum_duration": max_duration,
        "curriculum": curriculum,
        "electives": electives
    }
