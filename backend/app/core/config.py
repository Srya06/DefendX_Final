from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "DEFEND-X API"
    ENVIRONMENT: str = "local"
    # Provide a default SQLite DB for testing/development if URL is empty
    DATABASE_URL: str = "sqlite:///./test.db"
    AUTH_SECRET: str = "supersecret_default_do_not_use_in_prod"
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
