from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.utils.time import get_now_utc_string
from robotdegilim_xyz_backend.core.constants import S3Prefix

def enqueue_job(job_name: str, payload: dict | None = None) -> dict:
    """
    Attempts to enqueue a job into S3. 
    If a job of the same type is already pending, it deduplicates and skips.
    """
    # 1. Check for deduplication
    prefix = f"{S3Prefix.QUEUE}{job_name}_"
    existing_files = s3_client.list_files(prefix)
    
    if existing_files:
        # Job is already queued, maintain its original spot in line
        return {
            "status": "already_queued", 
            "message": f"A '{job_name}' job is already pending in the queue."
        }
        
    # 2. Generate a visual timestamp for the filename
    timestamp = get_now_utc_string()
    file_key = f"{S3Prefix.QUEUE}{job_name}_{timestamp}.pending"
    
    # 3. Upload the ticket to reserve the spot
    s3_client.upload_json(file_key, payload)
    
    return {
        "status": "queued",
        "message": f"Successfully queued '{job_name}' job."
    }
