from datetime import datetime, timezone

def get_now_utc_string() -> str:
    """
    Returns the current UTC time as a formatted string (e.g., 20260830_213500).
    Used consistently across the app for naming S3 queue and state files.
    """
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
