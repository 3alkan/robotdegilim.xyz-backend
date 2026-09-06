from fastapi import APIRouter
from robotdegilim_xyz_backend.services.queue_service import enqueue_job
from robotdegilim_xyz_backend.schemas.job import JobResponse

router = APIRouter()

@router.post("/scrape_courses", response_model=JobResponse)
def trigger_scrape_courses_job():
    """
    Enqueue the main courses scraping job to be processed by a worker.
    """
    return enqueue_job(job_name="scrape_courses")

@router.post("/scrape_programs", response_model=JobResponse)
def trigger_scrape_programs_job():
    """
    Enqueue the programs scraping job to be processed by a worker.
    """
    return enqueue_job(job_name="scrape_programs")
