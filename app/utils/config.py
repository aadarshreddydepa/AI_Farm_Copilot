# backend/app/utils/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # concurrency limits
    API_CONCURRENCY_LIMIT: int = 8
    API_TIMEOUT_SECONDS: int = 10
    TRANSlator_CACHE_SIZE: int = 512

    # Example API keys (set these in env)
    WEATHER_API_KEY: str | None = None
    CROP_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
