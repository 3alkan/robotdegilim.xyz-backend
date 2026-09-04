from enum import Enum

class S3Prefix(str, Enum):
    """S3 directory prefixes."""
    QUEUE = "queue/"
    JOB_STATES = "job-states/"
    LOCKS = "locks/"
    DATA = "data/"

class GlobalLock(str, Enum):
    """Global system lock files."""
    WORKER = "locks/worker.lock"

class SISConstants(str, Enum):
    """Constants related to the METU SIS website."""
    BASE_URL = "https://sis.metu.edu.tr"
