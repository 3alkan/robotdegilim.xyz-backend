from datetime import datetime
import pytz
from robotdegilim_xyz_backend.core.config import get_settings

settings = get_settings()

def get_now_string() -> str:
    """
    Returns the current configured timezone time as a formatted string (e.g., 20260830_213500).
    Used consistently across the app for naming S3 queue and state files.
    """
    app_tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(app_tz).strftime("%Y%m%d_%H%M%S")

def get_now_iso_string() -> str:
    """
    Returns the current time in the configured timezone in ISO 8601 format.
    Ideal for JSON metadata that frontends will consume.
    """
    app_tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(app_tz).isoformat()
