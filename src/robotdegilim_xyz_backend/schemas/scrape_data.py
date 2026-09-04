from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class CourseCredits(BaseModel):
    total: float
    ects: float
    lab: float
    theory: float
    application: float

class Capacity(BaseModel):
    total: int
    exchange: int
    exchange_used: int

class RangeFloat(BaseModel):
    min: float
    max: float

class RangeInt(BaseModel):
    min: int
    max: int

class Schedule(BaseModel):
    day: str
    start_hour: str
    end_hour: str
    classroom: str
    building: str

class Instructor(BaseModel):
    name: str
    title: str

class Criteria(BaseModel):
    given_dept: str
    start_char: str
    end_char: str
    cgpa: RangeFloat
    year: RangeInt
    start_grade: str
    end_grade: str

class Section(BaseModel):
    section_number: int
    capacity: Capacity
    schedule: List[Schedule]
    instructors: List[Instructor]
    criteria: List[Criteria]

class Course(BaseModel):
    code: str
    name: str
    credits: CourseCredits
    is_service_course: bool
    level: str
    type: str
    sections: List[Section]

class Program(BaseModel):
    short_name: str
    name: str
    courses: List[Course] = Field(default_factory=list)

class Metadata(BaseModel):
    semester_code: str
    semester_name: str
    updated_at: str

class ScrapeData(BaseModel):
    metadata: Metadata
    programs: Dict[str, Program]
