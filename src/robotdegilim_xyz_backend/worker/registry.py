from datetime import timedelta
from robotdegilim_xyz_backend.jobs.scrape_courses.run import run_scrape_courses

# This dictionary maps job names to their handler functions.
# If a threshold is None, the job will NEVER auto-schedule (manual trigger only).

JOB_REGISTRY = {
    "scrape_courses": {
        "handler": run_scrape_courses,
        "auto_run_threshold": timedelta(hours=12)
    },
    # Future jobs can simply be added here!
}
