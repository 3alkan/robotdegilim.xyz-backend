import time
import random
import logging
from typing import Any
from curl_cffi import requests
from robotdegilim_xyz_backend.core.exceptions import AppException
from robotdegilim_xyz_backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class HumanizedClient:
    """
    Project-wide HTTP client designed to bypass enterprise firewalls (Level 1 + Level 3).
    Implements perfect Chrome headers (via curl-cffi), session continuity, randomized human delays, and backoff retries.
    """
    def __init__(self):
        # Level 3: Perfect Cryptographic Spoofing + Cookie Continuity
        self.session = requests.Session(impersonate=settings.HUMANIZED_CLIENT_BROWSER)
        
        # Level 1 Configurations
        self.min_delay = settings.HUMANIZED_CLIENT_MIN_DELAY_SEC
        self.max_delay = settings.HUMANIZED_CLIENT_MAX_DELAY_SEC
        self.max_retries = settings.HUMANIZED_CLIENT_MAX_RETRIES
        
    def _apply_jitter(self):
        """Forces a random sleep to perfectly simulate human reading/clicking times."""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"Anti-ban jitter: Sleeping for {delay:.2f}s...")
        time.sleep(delay)
        
    def _execute_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        for attempt in range(1, self.max_retries + 1):
            self._apply_jitter()
            
            try:
                response = self.session.request(method, url, timeout=30.0, **kwargs)
                
                # Check for rate limiting
                if response.status_code in (429, 503):
                    logger.warning(f"Rate limited ({response.status_code}) on {url}. Backing off for 30 seconds...")
                    time.sleep(30)
                    continue
                    
                response.raise_for_status()
                return response
                
            except requests.errors.RequestsError as e:
                logger.warning(f"Network error on {url} (Attempt {attempt}/{self.max_retries}): {e}")
                if attempt == self.max_retries:
                    raise AppException(detail=f"Network failed after {self.max_retries} attempts: {url}", status_code=502)
                
                # Brief pause before retrying a broken connection
                time.sleep(5)
                
        # If we exhausted retries (e.g. 429s over and over)
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts.")
        raise AppException(detail=f"Failed to fetch {url}", status_code=502)

    def get(self, url: str, **kwargs) -> requests.Response:
        return self._execute_with_retry("GET", url, **kwargs)
        
    def post(self, url: str, **kwargs) -> requests.Response:
        return self._execute_with_retry("POST", url, **kwargs)

# Global singleton to be imported by all background jobs
human_client = HumanizedClient()
