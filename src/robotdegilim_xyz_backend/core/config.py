from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "robotdegilim.xyz API"
    PROJECT_DESCRIPTION: str = "Backend for robotdegilim.xyz"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS Settings (can be parsed from a string like "http://localhost,https://example.com")
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # S3 Configuration
    S3_BUCKET: str
    S3_ACCESS_KEY_ID: str
    S3_SECRET_ACCESS_KEY: str
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    LOG_TO_FILE: bool = False
    LOG_FILE_PATH: str = "logs/app.log"
    
    # Worker Configuration
    WORKER_POLL_INTERVAL: int = 10
    
    # Anti-Ban / HumanizedClient Configuration
    HUMANIZED_CLIENT_MIN_DELAY_SEC: float = 1.5
    HUMANIZED_CLIENT_MAX_DELAY_SEC: float = 3.5
    HUMANIZED_CLIENT_MAX_RETRIES: int = 3
    HUMANIZED_CLIENT_BROWSER: str = "chrome120"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings object.
    """
    return Settings()
