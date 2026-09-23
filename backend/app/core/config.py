from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DEFEND-X API"
    # Provide a default SQLite DB for testing/development if URL is empty
    DATABASE_URL: str = "sqlite:///./test.db"
    AUTH_SECRET: str = "supersecret_default_do_not_use_in_prod"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
