from datetime import timedelta
from robotdegilim_xyz_backend.jobs.scrape_courses.run import run_scrape_courses
from robotdegilim_xyz_backend.jobs.scrape_programs.run import run_scrape_programs

# This dictionary maps job names to their handler functions.
# If a threshold is None, the job will NEVER auto-schedule (manual trigger only).

JOB_REGISTRY = {
    "scrape_courses": {
        "handler": run_scrape_courses,
        "auto_run_threshold": timedelta(hours=12)
    },
    "scrape_programs": {
        "handler": run_scrape_programs,
        "auto_run_threshold": timedelta(hours=24)
    },
    # Future jobs can simply be added here!
}
