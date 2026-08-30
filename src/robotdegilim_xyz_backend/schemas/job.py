from pydantic import BaseModel, Field

class JobResponse(BaseModel):
    """
    Standard response model for all job queuing operations.
    """
    status: str = Field(..., description="The status of the job request (e.g., 'queued', 'already_queued')")
    message: str = Field(..., description="A detailed message about the job status")
