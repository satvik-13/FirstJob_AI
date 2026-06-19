from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str
    anthropic_base_url: str = "https://api.anthropic.com"

    # RapidAPI
    rapidapi_key: str

    # Hunter.io
    hunter_api_key: Optional[str] = None

    # Google
    google_client_id: str
    google_client_secret: str

    # Database
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/firstjob"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    secret_key: str
    frontend_url: str = "http://localhost:3000"
    environment: str = "development"
    app_name: str = "FirstJob"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
