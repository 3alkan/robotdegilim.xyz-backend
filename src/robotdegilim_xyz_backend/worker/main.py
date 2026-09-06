import time
import logging
from datetime import datetime, timezone

from robotdegilim_xyz_backend.core.logging import setup_logging
from robotdegilim_xyz_backend.core.config import get_settings
from robotdegilim_xyz_backend.clients.s3_client import s3_client
from robotdegilim_xyz_backend.worker.registry import JOB_REGISTRY
from robotdegilim_xyz_backend.utils.time import get_now_string
from robotdegilim_xyz_backend.core.constants import S3Prefix, GlobalLock
from robotdegilim_xyz_backend.services.queue_service import enqueue_job

logger = logging.getLogger(__name__)
settings = get_settings()

def process_queue() -> bool:
    """Checks the queue and runs the oldest pending job. Returns True if a job was run."""
    pending_files = s3_client.list_files(S3Prefix.QUEUE.value)
    if not pending_files:
        return False
        
    # Sort by oldest first based on S3 LastModified timestamp
    pending_files.sort(key=lambda x: x["last_modified"])
    target_job = pending_files[0]
    file_key = target_job["key"]
    
    # Extract job name from filename: queue/scrape_courses_20260830_100000.pending -> scrape_courses
    filename = file_key.split("/")[-1]
    job_name = filename.rsplit("_", 2)[0]
    
    if job_name not in JOB_REGISTRY:
        logger.error(f"Unknown job '{job_name}' found in queue. Deleting ticket.")
        s3_client.delete(key=file_key)
        return False
        
    logger.info(f"Dequeuing requested job: {job_name}")
    s3_client.delete(key=file_key)  # Remove from queue
    
    _execute_job(job_name)
    return True


def process_auto_scheduler() -> bool:
    """Checks job-states/ and enqueues jobs that exceed their threshold. Returns True if any were enqueued."""
    now = datetime.now(timezone.utc)
    enqueued_any = False
    
    for job_name, config in JOB_REGISTRY.items():
        threshold = config.get("auto_run_threshold")
        if not threshold:
            continue
            
        # Look for any state file (success or failed) for this job
        states = s3_client.list_files(f"{S3Prefix.JOB_STATES.value}{job_name}_")
        
        needs_run = False
        if not states:
            logger.info(f"Auto-scheduler: '{job_name}' never run before. Enqueuing.")
            needs_run = True
        else:
            # Get the absolute most recent run
            states.sort(key=lambda x: x["last_modified"], reverse=True)
            newest_state = states[0]
            time_since_last_run = now - newest_state["last_modified"]
            
            if time_since_last_run > threshold:
                logger.info(f"Auto-scheduler: '{job_name}' exceeded threshold. Enqueuing.")
                needs_run = True
                
        if needs_run:
            # Inject it into the standard queue instead of running it immediately
            enqueue_job(job_name, payload={"source": "auto_scheduler"})
            enqueued_any = True
            
    return enqueued_any

def _execute_job(job_name: str):
    """Executes the job and strictly manages the job-states file lifecycle."""
    handler = JOB_REGISTRY[job_name]["handler"]
    status_ext = "success"
    
    try:
        logger.info(f"Executing handler for '{job_name}'...")
        handler()
    except Exception as e:
        logger.exception(f"Job '{job_name}' failed with an error: {e}")
        status_ext = "failed"
    finally:
        # Wipe old state files (so there is only ever 1 file per job type)
        s3_client.delete(prefix=f"{S3Prefix.JOB_STATES.value}{job_name}_")
        
        # Upload the new state file with the exact current timestamp in the name
        timestamp = get_now_string()
        new_state_file = f"{S3Prefix.JOB_STATES.value}{job_name}_{timestamp}.{status_ext}"
        s3_client.upload_json(new_state_file)
        logger.info(f"Updated job state: {new_state_file}")

def main_loop():
    logger.info("Worker started. Polling S3 for jobs...")
    
    while True:
        try:
            if s3_client.file_exists(GlobalLock.WORKER.value):
                # Another worker is busy, or the lock is stuck.
                time.sleep(settings.WORKER_POLL_INTERVAL)
                continue
                
            # Claim the global lock
            s3_client.upload_json(GlobalLock.WORKER.value, {"locked_by": "worker", "time": get_now_string()})
            
            try:
                # 1. Always prioritize the manual queue
                did_work = process_queue()
                
                # 2. If queue is empty, check the auto-scheduler
                if not did_work:
                    process_auto_scheduler()
            finally:
                # 3. ALWAYS release the lock, even if a job crashed
                s3_client.delete(key=GlobalLock.WORKER.value)
                
        except Exception as e:
            logger.error(f"Worker loop encountered a critical error: {e}")
            
        time.sleep(settings.WORKER_POLL_INTERVAL)

if __name__ == "__main__":
    setup_logging()
    main_loop()
