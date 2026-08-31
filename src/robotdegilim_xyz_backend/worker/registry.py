from datetime import timedelta
from robotdegilim_xyz_backend.jobs.scrape.run import run_scrape

# The Central Job Registry
# Maps a job name to its execution function and auto-run threshold.
# If a threshold is None, the job will NEVER auto-schedule (manual trigger only).

JOB_REGISTRY = {
    "scrape": {
        "handler": run_scrape,
        "auto_run_threshold": timedelta(hours=12)
    },
    # Future jobs can simply be added here!
}
