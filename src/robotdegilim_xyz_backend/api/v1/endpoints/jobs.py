from fastapi import APIRouter
from robotdegilim_xyz_backend.services.queue_service import enqueue_job
from robotdegilim_xyz_backend.schemas.job import JobResponse

router = APIRouter()

@router.post("/scrape", response_model=JobResponse)
def trigger_scrape_job():
    """
    Enqueue the main scraping job to be processed by a worker.
    """
    return enqueue_job(job_name="scrape")
