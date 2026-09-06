from pydantic import BaseModel, Field
from typing import List, Dict
from enum import IntEnum

# ==============================================================================
# THE METU SIS PROGRAM KEY ANATOMY
# ==============================================================================
# Every program in the METU SIS backend is uniquely identified by a 4-part key.
# This key is formatted as: {ProgramCode}|{ProgramType}|{EducationLevel}|{DegreeType}
# 
# 1. ProgramCode: The program's code (Note: This can differ from the base dept code! 
#                 e.g., '571' is CENG Major, but '57120' is CENG Double Major, 
#                 and '57130' is CENG Minor).
#
# 2. ProgramType: 1 = MAJOR, 2 = DOUBLE MAJOR, 3 = MINOR
#
# 3. EducationLevel: 
#    - 1 = Bachelor's
#    - 61 = Master's (Compensatory)
#    - 62 = Master's (with thesis)
#    - 63 = Master's (non-thesis)
#    - 71 = Post Master's Doctoral (Compensatory)
#    - 72 = Doctoral
#    - 81 = Post- Bachelor's Doctoral (Compensatory)
#    - 83 = Post- Bachelor's Doctoral
#    - 91 = Non- Thesis Master's (Evening) (Compensatory)
#    - 93 = Non- Thesis Master's (Evening)
#
# 4. DegreeType: 1 = Bachelor's, 2 = Master's, 3 = Doctoral
#
# Example: '571|1|62|2' represents CENG | MAJOR | Master's (with thesis) | Master's
# ==============================================================================

class ProgramType(IntEnum):
    MAJOR = 1
    DOUBLE_MAJOR = 2
    MINOR = 3

class EducationLevel(IntEnum):
    BACHELORS = 1
    MASTERS_COMPENSATORY = 61
    MASTERS_WITH_THESIS = 62
    MASTERS_NON_THESIS = 63
    POST_MASTERS_DOCTORAL_COMPENSATORY = 71
    DOCTORAL = 72
    POST_BACHELORS_DOCTORAL_COMPENSATORY = 81
    POST_BACHELORS_DOCTORAL = 83
    NON_THESIS_MASTERS_EVENING_COMPENSATORY = 91
    NON_THESIS_MASTERS_EVENING = 93

class DegreeType(IntEnum):
    BACHELORS = 1
    MASTERS = 2
    DOCTORAL = 3

class SisProgramKey(BaseModel):
    program_code: str
    program_type: ProgramType
    education_level: EducationLevel
    degree_type: DegreeType

    @classmethod
    def from_string(cls, sis_key: str) -> "SisProgramKey":
        parts = sis_key.split("|")
        return cls(
            program_code=parts[0],
            program_type=ProgramType(int(parts[1])),
            education_level=EducationLevel(int(parts[2])),
            degree_type=DegreeType(int(parts[3]))
        )

class CurriculumCourse(BaseModel):
    code: str
    name: str
    metu_credit: float
    ects_credit: float
    is_elective: bool

class Semester(BaseModel):
    semester_number: int
    courses: List[CurriculumCourse]

class ElectiveCourse(BaseModel):
    code: str
    name: str
    category: str

class ProgramDetails(BaseModel):
    # Core Keys
    program_key: str
    
    # General Info
    campus_long_name: str
    campus_short_name: str
    program_code: str
    department_code: str
    short_name: str
    long_name: str
    program_type: str
    faculty_name: str
    institute_name: str
    education_type: str
    education_level: str
    administrator: str
    osym_code: str
    
    # From Program Summary Infobox
    minimum_total_credit: float
    overload: float
    degree: str
    minimum_duration: int
    maximum_duration: int

    # The Grid
    curriculum: Dict[int, Semester]

    # Available Electives
    electives: List[ElectiveCourse]

class ScrapeProgramsData(BaseModel):
    updated_at: str
    programs: Dict[str, ProgramDetails] = Field(default_factory=dict)
